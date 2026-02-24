#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from cStringIO import StringIO
from flask import Blueprint, session, current_app, request, jsonify, send_file, url_for, abort, redirect
from uuid import uuid4, UUID
import base64
import json
import zipfile
from cStringIO import StringIO
from uuid import uuid4

from flask import Blueprint
from flask import jsonify, request, send_file, current_app, session
from PIL import Image
from PIL.TiffImagePlugin import TiffImageFile

import psycopg2

import utils
from functions import no_preview_image

import config
import views
from const import pfsp2fpc, pfsp

from NIST.fingerprint.labels import SEGMENTS_POSITION_CODE as segments_position_code

afis_view = Blueprint( "afis", __name__, template_folder = "templates" )

@afis_view.route( "/afis/list/targets" )
@utils.decorator.login_required
def list_folders():
    user_id = session.get( "user_id", None )
    
    sql = """
        SELECT DISTINCT ON ( cnm_assignment.folder_uuid, tmp.donor_id, tmp.pc )
            cnm_assignment.folder_uuid,
            tmp.*
        FROM cnm_assignment
        LEFT JOIN cnm_folder ON cnm_assignment.folder_uuid = cnm_folder.uuid
        LEFT JOIN (
            SELECT DISTINCT ON ( donor_id, pc ) *
            FROM donor_segments_v
        ) AS tmp ON cnm_folder.donor_id = tmp.donor_id AND cnm_folder.pc = tmp.pc
        
        WHERE cnm_assignment.user_id = %s
        
        ORDER BY
            cnm_assignment.folder_uuid
    """
    folder_list = config.db.query_fetchall( sql, ( user_id, ) )
    
    return utils.template.my_render_template(
        "afis/user/folder_list.html",
        folder_list = folder_list
    )

def get_sql_list_incidental_marks_for_user( filter_submission_uuid = False ):
    sql = """
        SELECT
            files_v.uuid,
            submissions.uuid AS donor_uuid
        FROM ( """ + get_sql_list_deduplicated_donors_for_marks_for_user() + """ ) AS deduplicated_donor_list
        LEFT JOIN submissions ON deduplicated_donor_list.donor_id = submissions.donor_id
        LEFT JOIN files_v ON files_v.folder = submissions.id
        LEFT JOIN files_type ON files_v.type = files_type.id
        WHERE
            files_type.name = 'mark_incidental'
    """
    
    if filter_submission_uuid:
        sql += " AND deduplicated_donor_list.donor_uuid = %s"
    
    return sql

def get_sql_list_deduplicated_donors_for_marks_for_user():
    sql = """
        SELECT DISTINCT ON ( donor_id )
            cnm_folder.donor_id,
            submissions.uuid AS donor_uuid
        FROM cnm_assignment
        LEFT JOIN cnm_folder ON cnm_assignment.folder_uuid = cnm_folder.uuid
        LEFT JOIN cnm_assignment_type ON cnm_assignment.assignment_type = cnm_assignment_type.id
        LEFT JOIN submissions ON cnm_folder.donor_id = submissions.id
        WHERE
            cnm_assignment.user_id = %s AND
            cnm_assignment_type.name = 'mark'
    """
    return sql

@afis_view.route( "/afis/incidental/donors/list" )
@utils.decorator.login_required
def list_donors_incidental():
    user_id = session.get( "user_id", None )
    
    sql = get_sql_list_deduplicated_donors_for_marks_for_user()
    donor_list_tmp = config.db.query_fetchall( sql, ( user_id, ) )
    donor_list = []
    
    for donor in donor_list_tmp:
        tmp = dict( donor )
        tmp[ "derived_uuid" ] = utils.uuid_utils.derive_uuid_from_uuid( donor[ "donor_uuid" ], 0 )
        
        donor_list.append( tmp )
    
    donor_list.sort()
    
    return utils.template.my_render_template(
        "afis/user/incidental_donor_list.html",
        donor_list = donor_list,
    )

def get_submission_uuid_from_derived_uuid( derived_uuid ):
    sql = "SELECT uuid FROM submissions"
    uuid_list = config.db.query_fetchall( sql )
    
    for submission in uuid_list:
        if utils.uuid_utils.derive_uuid_from_uuid( submission[ "uuid" ], 0 ) == derived_uuid:
            return submission[ "uuid" ]
        
    else:
        return None

@afis_view.route( "/afis/incidental/donor/<uuid>/list" )
@utils.decorator.login_required
def list_incidentals( uuid ):
    user_id = session.get( "user_id", None )

    # Get the list of all the marks related to all the donors where at least one target mark is assigned to the afis user
    sql = get_sql_list_incidental_marks_for_user( True )
    submission_uuid = get_submission_uuid_from_derived_uuid( uuid )
    data = ( user_id, submission_uuid, )
    
    incidental_mark_list = config.db.query_fetchall( sql, data )
    
    #
    return utils.template.my_render_template(
        "afis/user/incidental_list.html",
        incidental_mark_list = incidental_mark_list,
        donor_uuid = uuid,
    )

@afis_view.route( "/admin/target/<submission_id>/<pc>/new" )
@utils.decorator.admin_required
def admin_create_new_target_and_redirect( submission_id, pc ):
    sql = "SELECT donor_id FROM submissions WHERE uuid = %s"
    donor_id = config.db.query_fetchone( sql, ( submission_id, ) )[ "donor_id" ]
    pc = int( pc )
    
    target_uuid = str( uuid4() )
    
    sql = utils.sql.sql_insert_generate( "cnm_folder", [ "uuid", "pc", "donor_id" ], "id" )
    config.db.query_fetchone( sql, ( target_uuid, pc, donor_id, ) )
    
    return redirect( url_for( "afis.admin_show_target", uuid = target_uuid ) )

@afis_view.route( "/admin/target/<uuid>" )
@utils.decorator.admin_required
def admin_show_target( uuid ):
    return show_folder_inner( uuid, True )

@afis_view.route( "/afis/<uuid>" )
@utils.decorator.login_required
def show_folder( uuid ):
    return show_folder_inner( uuid, False )

@afis_view.route( "/afis/incidental/<uuid>" )
@utils.decorator.login_required
def show_incidental_folder( uuid ):
    cnm_list = get_cnm_list_for_target_uuid( uuid, False )
    
    return utils.template.my_render_template(
        "afis/user/incidental_details.html",
        uuid = uuid,
        cnm_list = cnm_list,
    )

def get_count_files_for_target_folder_for_user( uuid, file_type ):
    sql = """
        SELECT count(*) AS count
        FROM cnm_assignment
        LEFT JOIN cnm_assignment_type ON cnm_assignment.assignment_type = cnm_assignment_type.id
        WHERE
            cnm_assignment.folder_uuid = %s AND
            cnm_assignment.user_id = %s AND
            cnm_assignment_type.name = %s
    """
    nb = config.db.query_fetchone( sql, ( uuid, session.get( "user_id", False ), file_type, ) )[ "count" ]
    return int( nb )

def get_segment_list_for_target_folder( uuid, admin = True ):
    if not admin and get_count_files_for_target_folder_for_user( uuid, "reference" ) == 0:
        return None
    
    else:
        sql = """
            SELECT
                cnm_folder.uuid AS folder_uuid,
                donor_segments_v.*
            FROM cnm_folder
            
            LEFT JOIN fingers_same ON cnm_folder.pc = fingers_same.base_finger
            RIGHT JOIN donor_segments_v ON
                cnm_folder.donor_id = donor_segments_v.donor_id AND
                fingers_same.target = donor_segments_v.pc
            
            WHERE cnm_folder.uuid = %s
            
            ORDER BY
                donor_segments_v.donor_id ASC,
                donor_segments_v.pc ASC
        """
        return config.db.query_fetchall( sql, ( uuid, ) )

def get_marks_list_for_incidental_folder( sub_uuid, target_uuid, admin = True):
    if not admin and get_count_files_for_target_folder_for_user( target_uuid, "mark" ) == 0:
        return None
    else:
        sql = """
            SELECT
                files_v.uuid,
                files_v.resolution,
                files_v.width,
                files_v.height,
                mark_info.pfsp
            FROM submissions
            LEFT JOIN files_v ON submissions.id = files_v.folder
            LEFT JOIN files_type ON files_v.type = files_type.id
            LEFT JOIN mark_info ON files_v.uuid = mark_info.uuid
            WHERE submissions.uuid = %s
        """

        marks_list = config.db.query_fetchall( sql, ( sub_uuid, ) )
        return marks_list

def get_marks_list_for_target_folder( uuid, admin = True, mark_type = [ "mark_target", "mark_incidental" ] ):
    if not admin and get_count_files_for_target_folder_for_user( uuid, "mark" ) == 0:
        return None
    
    else:
        # Select the type of marks to include in the list
        sql = """
            SELECT
                files_v.uuid,
                files_v.resolution,
                files_v.width,
                files_v.height,
                mark_info.pfsp
            FROM cnm_folder
            LEFT JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
            LEFT JOIN files_v ON submissions.id = files_v.folder
            LEFT JOIN files_type ON files_v.type = files_type.id
            LEFT JOIN mark_info ON files_v.uuid = mark_info.uuid
            WHERE
                cnm_folder.uuid = %s
        """
        
        if mark_type == None:
            mark_type = []
        if len( mark_type ) != 0:
            where_clause = [ "files_type.name = '{}'".format( mt ) for mt in mark_type ]
            where_clause = " OR ".join( where_clause )
            where_clause = " AND ( {} )".format( where_clause )
            sql += where_clause
        
        # Get the list of marks
        marks_list = []
        marks_list_tmp = config.db.query_fetchall( sql, ( uuid, ) )
        
        sql = "SELECT pc FROM cnm_folder WHERE uuid = %s"
        pc_success = False
        try:
            pc = config.db.query_fetchone( sql, ( uuid, ) )[ "pc" ]
            pc_success = True
        except:
            # no pc value exists
            return None
        if(pc_success):

            for m in marks_list_tmp:
                try:
                    for z in m[ "pfsp" ].split( "," ):
                        if pc in pfsp2fpc[ z ]:
                            marks_list.append( m )
                            break
                except:
                    continue
                    
        return marks_list

def get_marks_list_for_exercise_folder( uuid ):
    sql = """
            SELECT
                files.uuid
            FROM exercises_folder
            LEFT JOIN files ON exercises_folder.mark = files.uuid
            WHERE
                exercises_folder.folder = %s
        """
    marks_list = []
    marks_list_tmp = config.db.query_fetchall( sql, ( uuid, ) )
    
    return marks_list_tmp
        
    
def get_annotation_list_for_target_folder( uuid, admin = True ):
    sql = """
        SELECT uuid
        FROM cnm_annotation
        WHERE
            folder_uuid = %s
    """
    return config.db.query_fetchall( sql, ( uuid, ) )

def get_target_folder_details( uuid ):
    sql = """
        SELECT
            submissions.uuid,
            cnm_folder.pc,
            users.username
        FROM cnm_folder
        INNER JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
        INNER JOIN users ON cnm_folder.donor_id = users.id
        WHERE cnm_folder.uuid = %s
    """
    return config.db.query_fetchone( sql, ( uuid, ) )

def show_folder_inner( uuid, admin ):
    """
        This function get all the data related to particular target
        (annotations, marks, refs and assignments), for admins and afis users.
    """
    
    # Redirect non-admins if not assigned to this folder
    if not admin:
        sql = "SELECT count(*) FROM cnm_assignment WHERE folder_uuid = %s AND user_id = %s"
        if config.db.query_fetchone( sql, ( uuid, session.get( "user_id" ), ) )[ "count" ] == 0:
            return redirect( url_for( "base.home" ) )
    
    # Get the annotations, references and marks lists
    segments_list = get_segment_list_for_target_folder( uuid, admin )
    annotation_list = get_annotation_list_for_target_folder( uuid, admin )
    marks_list = get_marks_list_for_target_folder( uuid, admin, [ "mark_target" ] )
    
    # Generic information
    details = get_target_folder_details( uuid )
    submission_id = details[ "uuid" ]
    pc = details[ "pc" ]
    username = details[ "username" ]
    
    finger_name = "{} (F{})".format( segments_position_code[ pc ], pc )
    
    # User assignments
    if admin:
        sql = r"""
            SELECT
                users.id,
                users.username
            FROM users
            LEFT JOIN account_type ON users.type = account_type.id
            WHERE account_type.name = 'AFIS'
            ORDER BY NULLIF( regexp_replace( username, '\D', '', 'g' ), '' )::int
        """
        all_afis_users = config.db.query_fetchall( sql )
        
        def get_user_assined( assignment_type ):
            sql = """
                SELECT
                    cnm_assignment.user_id AS id
                FROM cnm_assignment
                LEFT JOIN cnm_assignment_type ON cnm_assignment.assignment_type = cnm_assignment_type.id
                WHERE
                    cnm_assignment.folder_uuid = %s AND
                    cnm_assignment_type.name = '{}'
            """.format( assignment_type )
            return config.db.query_fetchall( sql, ( uuid, ) )
        
        users_assigned_refs = get_user_assined( "reference" )
        users_assigned_marks = get_user_assined( "mark" )
    
    else:
        submission_id = None
        finger_name = None
        username = None
        all_afis_users = None
        users_assigned_refs = []
        users_assigned_marks = []
    
    # List of cnm results
    if admin:
        cnm_result = get_cnm_list_for_target_uuid( uuid, True )
        
    else:
        cnm_result = None

    #
    return utils.template.my_render_template(
        "afis/shared/segment.html",
        target_uuid = uuid,
        segments_list = segments_list,
        annotation_list = annotation_list,
        marks_list = marks_list,
        submission_id = submission_id,
        username = username,
        finger_name = finger_name,
        all_afis_users = all_afis_users,
        users_assigned_refs = users_assigned_refs,
        users_assigned_marks = users_assigned_marks,
        cnm_result = cnm_result,
    )

@afis_view.route( "/admin/target/<uuid>/new_illustration", methods = [ "POST" ] )
@utils.decorator.admin_required
def admin_add_illustration( uuid ):
    try:
        sql = """
            SELECT submissions.uuid
            FROM cnm_folder
            LEFT JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
            WHERE cnm_folder.uuid = %s
        """
        donor_id = config.db.query_fetchone( sql, ( uuid, ) )[ "uuid" ]
        
        uploaded_file = request.files[ "file" ]
        
        fp = StringIO()
        uploaded_file.save( fp )
        fp.seek( 0 )
        
        file_data = fp.getvalue()
        file_data = base64.b64encode( file_data )
        file_data = utils.encryption.do_encrypt_dek( file_data, donor_id )
        
        sql = utils.sql.sql_insert_generate(
            "cnm_annotation",
            [ "uuid", "folder_uuid", "data" ],
            "id"
        )
        data = ( str( uuid4() ), uuid, file_data, )
        config.db.query_fetchone( sql, data )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": False
        } )

@afis_view.route( "/admin/target/<folder_uuid>/target/annotation/delete", methods = [ "POST" ] )
@utils.decorator.admin_required
def admin_delete_annotation( folder_uuid ):
    try:
        illustration_uuid = request.form.get( "uuid" )
        sql = "DELETE FROM cnm_annotation WHERE folder_uuid = %s AND uuid = %s"
        config.db.query( sql, ( folder_uuid, illustration_uuid, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/afis/<uuid>/download/mark" )
@utils.decorator.login_required
def download_mark( uuid ):
    # Check for access rights
    sql = get_sql_list_incidental_marks_for_user()
    marks = config.db.query_fetchall( sql, ( session.get( "user_id" ), ) )
    marks = [ m[ "uuid" ] for m in marks ]
    
    if not uuid in marks:
        return abort( 403 )
    
    else:
        # Set the filename
        short_uuid = uuid[ 0:18 ]
        filename = "{}.tiff".format( short_uuid, )
        
        # Get the image
        submission_id = views.images.get_submission_uuid_for_file( uuid )
        img, _ = views.images.image_serve( "files", uuid, submission_id )
        img = views.images.image_tatoo( img, uuid )
        
        # Convert the image to be returned
        buff = utils.images.pil2buffer( img, "TIFF" )
        
        return send_file(
            buff,
            mimetype = "image/tiff",
            as_attachment = True,
            attachment_filename = filename,
        )

@afis_view.route( "/afis/<uuid>/download_exercise")
@utils.decorator.login_required
def download_exercise_folder( uuid ):
    short_uuid = uuid[ 0:18 ]
    current_app.logger.info("ATTEMPTING DOWNLOAD OF " + str(uuid))
    exercise_list = get_marks_list_for_exercise_folder( uuid )
    zipbuffer = StringIO()
    with zipfile.ZipFile( zipbuffer, "w", zipfile.ZIP_DEFLATED ) as fp:
        for mid in exercise_list:
            file_id = mid[0]
            short_file_id = file_id[ 0:18 ]
                
            submission_id = views.images.get_submission_uuid_for_file( file_id )
            img, _ = views.images.image_serve( "files", file_id, submission_id )
            img = views.images.image_tatoo( img, file_id )
                
            buff = utils.images.pil2buffer( img, "TIFF" )
            fp.writestr(
                "{}_mark_{}.tiff".format( short_uuid, short_file_id ),
                buff.getvalue()
            )
            
    zipbuffer.seek( 0 )
    current_app.logger.info("ZIP FILE READY")
    return send_file(
        zipbuffer,
        attachment_filename = "{}.zip".format( short_uuid ),
        as_attachment = True
    )
    

@afis_view.route( "/afis/<uuid>/download" )
@utils.decorator.login_required
def download_target_folder( uuid ):
    short_uuid = uuid[ 0:18 ]
    annotation_list = get_annotation_list_for_target_folder( uuid, False )
    segments_list = get_segment_list_for_target_folder( uuid, False )
    marks_list = get_marks_list_for_target_folder( uuid, False, [ "mark_target" ] )
    exercise_list = ""
    zipbuffer = StringIO()
    
    with zipfile.ZipFile( zipbuffer, "w", zipfile.ZIP_DEFLATED ) as fp:
        if isinstance( annotation_list, list ):
            for fid in annotation_list:
                file_id = fid[ "uuid" ]
                short_file_id = file_id[ 0:18 ]
                
                submission_id = views.images.get_submission_uuid_for_annotation( file_id )
                
                img, _ = views.images.image_serve( "cnm_annotation", file_id, submission_id )
                img = views.images.image_tatoo( img, file_id )
                
                buff = utils.images.pil2buffer( img, "TIFF" )
                fp.writestr(
                    "{}_annotation_{}.tiff".format( short_uuid, short_file_id ),
                    buff.getvalue()
                )
                
        if isinstance( segments_list, list ):
            for sid in segments_list:
                file_id = sid[ "uuid" ]
                short_file_id = file_id[ 0:18 ]
                tenprint_id = sid[ "tenprint" ]
                pc = sid[ "pc" ]
                
                submission_id = views.images.get_submission_uuid_for_file( tenprint_id )
                
                img, _ = views.images.image_serve( "files_segments", ( tenprint_id, pc ), submission_id )
                img = views.images.image_tatoo( img, file_id )
                
                buff = utils.images.pil2buffer( img, "TIFF" )
                fp.writestr(
                    "{}_reference_{}.tiff".format( short_uuid, short_file_id ),
                    buff.getvalue()
                )
                
        if isinstance( marks_list, list ):
            for mid in marks_list:
                file_id = mid[ "uuid" ]
                short_file_id = file_id[ 0:18 ]
                
                submission_id = views.images.get_submission_uuid_for_file( file_id )
                img, _ = views.images.image_serve( "files", file_id, submission_id )
                img = views.images.image_tatoo( img, file_id )
                
                buff = utils.images.pil2buffer( img, "TIFF" )
                fp.writestr(
                    "{}_mark_{}.tiff".format( short_uuid, short_file_id ),
                    buff.getvalue()
                )
        if isinstance( exercise_list, list):
            for mid in exercise_list:
                file_id = mid[ "uuid" ]
                short_file_id = file_id[ 0:18 ]
                
                submission_id = views.images.get_submission_uuid_for_file( file_id )
                img, _ = views.images.image_serve( "files", file_id, submission_id )
                img = views.images.image_tatoo( img, file_id )
                
                buff = utils.images.pil2buffer( img, "TIFF" )
                fp.writestr(
                    "{}_mark_{}.tiff".format( short_uuid, short_file_id ),
                    buff.getvalue()
                )
            
    zipbuffer.seek( 0 )
    
    return send_file(
        zipbuffer,
        attachment_filename = "{}.zip".format( short_uuid ),
        as_attachment = True
    )

def get_cnm_list_for_target_uuid( uuid, admin ):
    sql = """
        SELECT
            cnm_result.uuid,
            cnm_result.nickname,
            tmp.uuid AS file_uuid,
            tmp.filetype_name
        FROM cnm_result
        LEFT JOIN (
            SELECT DISTINCT ON ( cnm_result )
                cnm_candidate.uuid,
                cnm_candidate.cnm_result,
                cnm_candidate_filetype.name AS filetype_name
            FROM cnm_candidate
            LEFT JOIN cnm_candidate_filetype ON cnm_candidate.file_type = cnm_candidate_filetype.id
            ORDER BY cnm_candidate.cnm_result, cnm_candidate.file_type ASC
        ) AS tmp ON cnm_result.uuid = tmp.cnm_result
        WHERE
            cnm_folder = %s
    """
    
    if admin:
        data = ( uuid, )
    else:
        sql += " AND uploader = %s"
        data = ( uuid, session.get( "user_id" ), )
        
    return config.db.query_fetchall( sql, data )
    
@afis_view.route( "/afis/<uuid>/upload/list" )
@utils.decorator.login_required
def upload_cnm_list_page( uuid ):
    cnm_result_list = get_cnm_list_for_target_uuid( uuid, False )
    
    for _, cnm_result in enumerate( cnm_result_list ):
        for key in [ "nickname" ]:
            cnm_result[ key ] = utils.encryption.do_decrypt_user_session( cnm_result[ key ] )
    
    return utils.template.my_render_template(
        "afis/user/upload_cnm_list.html",
        cnm_result_list = cnm_result_list,
        target_uuid = uuid,
    )

@afis_view.route( "/afis/<uuid>/upload/new/<target_type>" )
@utils.decorator.login_required
def new_cnm_case( uuid, target_type ):
    new_cnm_uuid = str( uuid4() )
    target_type = config.db.query_fetchone( "SELECT id FROM cnm_result_targettype WHERE name = %s", ( target_type, ) )[ "id" ]
    
    sql = utils.sql.sql_insert_generate(
        "cnm_result",
        [ "uuid", "cnm_folder", "uploader", "target_type" ],
        "id"
    )
    data = ( new_cnm_uuid, uuid, session.get( "user_id" ), target_type )
    config.db.query_fetchone( sql, data )
    
    return redirect( url_for( "afis.cnm_edit", target_uuid = uuid, cnm_uuid = new_cnm_uuid ) )

@afis_view.route( "/admin/afis/<target_uuid>/<cnm_uuid>" )
@utils.decorator.admin_required
def admin_cnm_edit( target_uuid, cnm_uuid ):
    return cnm_edit_inner( target_uuid, cnm_uuid, True )
    
@afis_view.route( "/afis/<target_uuid>/<cnm_uuid>" )
@utils.decorator.login_required
def cnm_edit( target_uuid, cnm_uuid ):
    return cnm_edit_inner( target_uuid, cnm_uuid, False )

def cnm_edit_inner( target_uuid, cnm_uuid, admin ):
    sql = """
        SELECT
            cnm_result.*,
            users.username AS uploader_username
        FROM cnm_result
        LEFT JOIN users ON cnm_result.uploader = users.id
        WHERE
            uuid = %s
    """
    
    if admin:
        data = ( cnm_uuid, )
        
    else:
        sql += " AND uploader = %s"
        data = ( cnm_uuid, session.get( "user_id" ), )
        
    cnm_result = config.db.query_fetchone( sql, data )
    
    if cnm_result == None and not admin:
        return redirect( url_for( "login.login" ) + "?" + request.path )
    
    else:
        for f in [ "nickname" ]:
            cnm_result[ f ] = utils.encryption.do_decrypt_user_session( cnm_result[ f ] )
        
        def get_cnm_list_files( file_type ):
            sql = """
                SELECT
                    uuid,
                    filename,
                    extension
                FROM cnm_candidate
                LEFT JOIN cnm_candidate_filetype ON cnm_candidate.file_type = cnm_candidate_filetype.id
                WHERE
                    cnm_result = %s AND
                    cnm_candidate_filetype.name = %s
            """
            uploaded_files = config.db.query_fetchall( sql, ( cnm_uuid, file_type, ) )

            for _, uploaded_file in enumerate( uploaded_files ):
                for key in [ "filename" ]:
                    uploaded_file[ key ] = utils.encryption.do_decrypt_user_session( uploaded_file[ key ] )
            
            return uploaded_files
        
        uploaded_cards = get_cnm_list_files( "card" )
        uploaded_screenshots = get_cnm_list_files( "screenshot" )
        
        sql = "SELECT * FROM cnm_result_quality"
        all_qualities = config.db.query_fetchall( sql )
        
        try:
            # Generic information for the target and donor
            details = get_target_folder_details( target_uuid )
            submission_uuid = details[ "uuid" ]
            pc = details[ "pc" ]
            username = details[ "username" ]
            finger_name = "{} (F{})".format( segments_position_code[ pc ], pc )
            target_type = "target"
            
        except:
            sql = """
                SELECT
                    submissions.uuid AS submission_uuid,
                    users.username
                FROM files
                LEFT JOIN submissions ON files.folder = submissions.id
                left join users on submissions.donor_id = users.id
                WHERE files.uuid = %s
            """
            details = config.db.query_fetchone( sql, ( target_uuid, ) )
            submission_uuid = details[ "submission_uuid" ]
            username = details[ "username" ]
            pc = None
            finger_name = target_uuid[ 0:18 ]
            target_type = "incidental"

        # List of marks for the corresponding donor
        mark_list = get_marks_list_for_target_folder( target_uuid, True )
        if(mark_list == None):
            mark_list = get_marks_list_for_incidental_folder( submission_uuid, target_uuid, admin = True)
        # Id for the first matched zone
        matched_pfsp = ""
        try:
            current_pfsp_id = cnm_result.get( "matched_pfsp", "" )
            matched_pfsp = current_pfsp_id
            current_pfsp_id = current_pfsp_id.split( "," )[ 0 ]
            current_pfsp_id = current_pfsp_id.split( "-" )[ 0 ]
            current_pfsp_id = current_pfsp_id.replace( "F", "" )
            current_pfsp_id = int( current_pfsp_id )
            
        except:
            current_pfsp_id = 0
            
        #
        return utils.template.my_render_template(
            "afis/shared/cnm_edit.html",
            target_uuid = target_uuid,
            cnm_uuid = cnm_uuid,
            cnm_result = cnm_result,
            current_pfsp_id = current_pfsp_id,
            uploaded_cards = uploaded_cards,
            uploaded_screenshots = uploaded_screenshots,
            all_qualities = all_qualities,
            pfsp_zones = pfsp.zones,
            submission_id = submission_uuid,
            username = username,
            finger_name = finger_name,
            target_type = target_type,
            mark_list = mark_list,
            matched_pfsp = matched_pfsp,
        )

@afis_view.route( "/afis/<target_uuid>/<cnm_uuid>/set_pfsp", methods = [ "POST" ] )
@utils.decorator.login_required
def cnm_set_pfsp( target_uuid, cnm_uuid ):
    try:
        pfsp = request.form.get( "pfsp", None )
        sql = """
            UPDATE cnm_result
            SET matched_pfsp = %s
            WHERE uuid = %s
        """
        config.db.query( sql, ( pfsp, cnm_uuid, ) )
        
        return jsonify( {
            "error": False,
            "data": pfsp
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/afis/<target_uuid>/<cnm_uuid>/<file_uuid>" )
@utils.decorator.login_required
def cnm_view_nist_file( target_uuid, cnm_uuid, file_uuid ):
    return cnm_view_nist_file_inner( target_uuid, cnm_uuid, file_uuid, False )

@afis_view.route( "/admin/afis/<target_uuid>/<cnm_uuid>/<file_uuid>" )
@utils.decorator.login_required
def admin_cnm_view_nist_file( target_uuid, cnm_uuid, file_uuid ):
    return cnm_view_nist_file_inner( target_uuid, cnm_uuid, file_uuid, True )

def cnm_view_nist_file_inner( target_uuid, cnm_uuid, file_uuid, admin ):
    sql = """
        SELECT nickname
        FROM cnm_result
        WHERE uuid = %s
    """
    cnm_nickname = config.db.query_fetchone( sql, ( cnm_uuid, ) )[ "nickname" ]
    cnm_nickname = utils.encryption.do_decrypt_user_session( cnm_nickname )
    
    sql = """
        SELECT filename
        FROM cnm_candidate
        WHERE uuid = %s
    """
    filename = config.db.query_fetchone( sql, ( file_uuid, ) )[ "filename" ]
    filename = utils.encryption.do_decrypt_user_session( filename )
    
    # Generic information for the target and donor
    details = get_target_folder_details( target_uuid )
    submission_uuid = details[ "uuid" ]
    pc = details[ "pc" ]
    username = details[ "username" ]
    finger_name = "{} (F{})".format( segments_position_code[ pc ], pc )
    
    return utils.template.my_render_template(
        "afis/shared/nist_view.html",
        segments_position_code = segments_position_code,
        target_uuid = target_uuid,
        cnm_uuid = cnm_uuid,
        file_uuid = file_uuid,
        cnm_nickname = cnm_nickname,
        filename = filename,
        username = username,
        finger_name = finger_name,
        submission_id = submission_uuid,
    )
    
@afis_view.route( "/afis/<target_uuid>/<cnm_uuid>/upload", methods = [ "POST" ] )
@utils.decorator.login_required
def upload_file( target_uuid, cnm_uuid ):
    try:
        uploaded_file = request.files[ "file" ]
        file_type = request.form.get( "file_type" )
        file_name = utils.encryption.do_encrypt_user_session( uploaded_file.filename )
        file_uuid = str( uuid4() )
        
        file_type_id = config.db.query_fetchone( "select id from cnm_candidate_filetype where name = %s", ( file_type, ) )[ "id" ]
        
        file_extension = request.form.get( "extension", None )
        if isinstance( file_extension, str ):
            file_extension = file_extension.lower()
        
        fp = StringIO()
        
        uploaded_file.save( fp )
        
        file_data = fp.getvalue()
        file_data = base64.b64encode( file_data )
        
        sql = utils.sql.sql_insert_generate(
            "cnm_candidate",
            [ "uuid", "data", "filename", "cnm_result", "creator", "extension", "file_type" ],
            "id"
        )
        data = (
            file_uuid,
            file_data,
            file_name,
            cnm_uuid,
            session.get( "user_id" ),
            file_extension,
            file_type_id,
        )
        config.db.query_fetchone( sql, data )
        
        return jsonify( {
            "error": False,
            "file_uuid": file_uuid
        } )
    
    except:
        return jsonify( {
            "error": True
        } )
    
@afis_view.route( "/afis/<target_uuid>/<cnm_uuid>/delete", methods = [ "POST" ] )
@utils.decorator.admin_required
def delete_file( target_uuid, cnm_uuid ):
    try:
        file_uuid = request.form.get( "file_uuid" )
        
        sql = "DELETE FROM cnm_candidate WHERE uuid = %s"
        config.db.query( sql, ( file_uuid, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/afis/<target_uuid>/delete", methods = [ "POST" ] )
@utils.decorator.admin_required
def delete_cnm_result( target_uuid ):
    try:
        cnm_uuid = request.form.get( "cnm_uuid" )
        sql = "DELETE FROM cnm_candidate WHERE cnm_result = %s"
        config.db.query( sql, ( cnm_uuid, ) )
        
        sql = "DELETE FROM cnm_result WHERE uuid = %s"
        config.db.query( sql, ( cnm_uuid, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )
    
@afis_view.route( "/afis/<target_uuid>/<cnm_uuid>/update_field", methods = [ "POST" ] )
@utils.decorator.login_required
def cnm_update_metadata( target_uuid, cnm_uuid ):
    field = request.form.get( "field", None )
    
    if field in [ "nickname", "db_size", "public_notes", "quality", "tags", "is_personal_cnm", "afis_rank", "is_a_good_cnm" ]:
        try:
            sql = """
                UPDATE cnm_result
                SET {} = %s
                WHERE uuid = %s
            """.format( field )
            
            data = request.form.get( "data", "" )
            if data == "":
                data = None
            
            if field in [ "nickname" ]:
                data = utils.encryption.do_encrypt_user_session( data )
            
            config.db.query( sql, ( data, cnm_uuid, ) )
            
            return jsonify( {
                "error": False
            } )
        
        except:
            return jsonify( {
                "error": True
            } )
        
    else:
        return jsonify( {
            "error": True
        } )
    
@afis_view.route( "/admin/<submission_uuid>/target/list" )
@utils.decorator.admin_required
def admin_show_target_list( submission_uuid ):
    sql = """
        SELECT DISTINCT ON ( donor_segments_v.pc )
            donor_segments_v.*,
            cnm_folder.uuid AS folder_uuid
        FROM donor_segments_v
        LEFT JOIN submissions ON submissions.donor_id = donor_segments_v.donor_id
        LEFT JOIN cnm_folder ON
            donor_segments_v.donor_id = cnm_folder.donor_id AND
            donor_segments_v.pc = cnm_folder.pc
        WHERE submissions.uuid = %s
    """
    segments_list = config.db.query_fetchall( sql, ( submission_uuid, ) )
    
    sql = """
        SELECT
            cnm_folder.pc
        FROM submissions
        LEFT JOIN cnm_folder ON submissions.donor_id = cnm_folder.donor_id
        LEFT JOIN cnm_annotation ON cnm_folder.uuid = cnm_annotation.folder_uuid
        WHERE
            submissions.uuid = %s AND
            cnm_annotation.data IS NOT NULL
        GROUP BY pc
    """
    annotations = config.db.query_fetchall( sql, ( submission_uuid, ) )
    annotations = [ a[ 'pc' ] for a in annotations ]
    
    sql = """
        SELECT username
        FROM users
        LEFT JOIN submissions ON users.id = submissions.donor_id
        WHERE submissions.uuid = %s
    """
    username = config.db.query_fetchone( sql, ( submission_uuid, ) )[ "username" ]
    
    return utils.template.my_render_template(
        "afis/admin/folder_list.html",
        segments_list = segments_list,
        annotations = annotations,
        segments_position_code = segments_position_code,
        username = username,
        submission_uuid = submission_uuid
    )
    
@afis_view.route( "/admin/afis/<target_uuid>/user/update", methods = [ "POST" ] )
@utils.decorator.admin_required
def admin_update_users_in_afis_folder( target_uuid ):
    try:
        users = request.form.get( "users" )
        users = json.loads( users )

        assignment_type = request.form.get( "type" )
        sql = "SELECT id FROM cnm_assignment_type WHERE name = %s"
        assignment_type_id = config.db.query_fetchone( sql, ( assignment_type, ) )[ "id" ]

        sql = """
            DELETE FROM cnm_assignment
            WHERE
                folder_uuid = %s AND
                assignment_type = %s
        """
        config.db.query( sql, ( target_uuid, assignment_type_id, ) )
            
        sql = utils.sql.sql_insert_generate(
            "cnm_assignment",
            [ "folder_uuid", "user_id", "assignment_type" ],
            "id"
        )
        for user in users:
            config.db.query_fetchone( sql, ( target_uuid, user, assignment_type_id, ) )
            
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/admin/afis/get_target_list" )
@utils.decorator.admin_required
def get_target_list():
    try:
        @utils.redis.redis_cache( 10 )
        def get_target_list_inner():
            sql = """
                SELECT
                    tmp.uuid,
                    tmp.donor_username,
                    tmp.pc,
                    tmp.nb,
                    users.username AS submitter_username
                FROM (
                    SELECT
                        cnm_folder.uuid,
                        users.username as donor_username,
                        users.id as donor_id,
                        cnm_folder.pc,
                        count( cnm_folder.uuid ) AS nb,
                        submissions.submitter_id
                    FROM cnm_annotation
                    LEFT JOIN cnm_folder ON cnm_annotation.folder_uuid = cnm_folder.uuid
                    LEFT JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
                    LEFT JOIN users ON users.id = submissions.donor_id
                    GROUP BY
                        cnm_folder.uuid,
                        cnm_folder.pc,
                        users.username,
                        users.id,
                        submissions.submitter_id
                ) AS tmp
                LEFT JOIN users ON tmp.submitter_id = users.id
                ORDER BY
                    tmp.donor_id,
                    tmp.pc
            """
            targets = config.db.query_fetchall( sql )
            headers = [ "uuid", "donor_username", "fpc", "count", "submitter_username" ]
            
            return targets, headers
        
        targets, headers = get_target_list_inner()
        
        return jsonify( {
            "error": False,
            "data": targets,
            "headers": headers
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/admin/afis/get_assignments" )
@utils.decorator.admin_required
def get_target_assignements():
    try:
        sql = """
            SELECT
                cnm_assignment.folder_uuid,
                cnm_assignment_type.name,
                users.username
            FROM cnm_assignment
            LEFT JOIN users ON cnm_assignment.user_id = users.id
            LEFT JOIN cnm_assignment_type ON cnm_assignment.assignment_type = cnm_assignment_type.id
        """
        assignments = config.db.query_fetchall( sql )

        return jsonify( {
            "error": False,
            "data": assignments,
            "headers": [ "folder_uuid", "type", "username" ]
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/admin/afis/get_afis_users" )
@utils.decorator.admin_required
def get_afis_users_list():
    try:
        @utils.redis.redis_cache( 10 )
        def get_afis_users_list_inner():
            sql = """
                SELECT
                    users.id,
                    users.username
                FROM users
                LEFT JOIN account_type ON users.type = account_type.id
                WHERE account_type.name = 'AFIS'
                ORDER BY users.id ASC
            """
            users_list = config.db.query_fetchall( sql )
            
            sql = """
                SELECT
                    username_id,
                    email
                FROM signin_requests
                LEFT JOIN account_type ON signin_requests.account_type = account_type.id
                WHERE account_type.name = 'AFIS'
            """
            afis_email_list = {}
            for u in config.db.query_fetchall( sql ):
                afis_email_list[ "afis_{}".format( u[ "username_id" ] ) ] = u[ "email" ]
            
            ret = []
            for user in users_list:
                tmp = [
                    user[ "id" ],
                    user[ "username" ],
                    afis_email_list[ user[ "username" ] ]
                ]
                ret.append( tmp )
                
            headers = [ "id", "username", "email" ]
            
            return ret, headers
        
        ret, headers = get_afis_users_list_inner()
        
        return jsonify( {
            "error": False,
            "data": ret,
            "headers": headers
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/admin/afis/batch_assign/do", methods = [ "POST" ] )
@utils.decorator.admin_required
def batch_assign_do():
    @utils.redis.redis_cache( 10 )
    def get_user_id( username ):
        return config.db.query_fetchone(
            "SELECT id FROM users WHERE username = %s",
            ( username, )
        )[ "id" ]

    @utils.redis.redis_cache( 60 )
    def get_assignments_types():
        ret = {}
        for a in config.db.query_fetchall( "SELECT * FROM cnm_assignment_type" ):
            ret[ a[ "name" ] ] = a[ "id" ]
        return ret
    
    try:
        config.db.query( "DELETE FROM cnm_assignment" )
        
        assignments_type_dict = get_assignments_types()
        
        sql_insert = utils.sql.sql_insert_generate(
            "cnm_assignment",
            [ "folder_uuid", "user_id", "assignment_type" ]
        )
        
        # Preprocess the data
        data = request.form.get( "data" )
        data = data.split( "\n" )
        data = set( data )
        
        # Parse and insert the data in the database
        for d in data:
            if d == "":
                continue
            
            uuid, assignment_type, username = d.split( ";" )
            if uuid == "folder_uuid":
                continue
            try:
                UUID( uuid, version = 4 )
            except:
                raise Exception( "not a valid uuid" )
            
            user_id = get_user_id( username )
            
            try:
                config.db.query(
                    sql_insert,
                    ( uuid, user_id, assignments_type_dict[ assignment_type ], )
                )
                
            # Check for UniqueViolation; This is done with the lookup() function to avoid the linter error
            except psycopg2.errors.lookup( "23505" ):
                continue
                
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@afis_view.route( "/admin/afis/batch_assign" )
@utils.decorator.admin_required
def batch_assign():
    return utils.template.my_render_template(
        "afis/admin/batch_assign.html"
    )

@afis_view.route( "/image/cnm_candidate/screenshot/<file_uuid>/preview" )
@utils.decorator.login_required
def screenshot_preview( file_uuid ):
    img, _ = views.images.image_serve( "cnm_candidate", file_uuid, None )
    
    if isinstance( img, TiffImageFile ):
        if not hasattr( img, "use_load_libtiff" ):
            img.use_load_libtiff = True
    
    if img == None:
        return abort( 404 )
    
    else:
        img.thumbnail( ( 800, 800 ) )
        
        buff = utils.images.pil2buffer( img, "JPEG" )
        return send_file( buff, mimetype = "image/jpeg" )
    
@afis_view.route( "/admin/afis/list_all" )
@utils.decorator.admin_required
def admin_list_all_cnm_candidates():
    sql = """
        SELECT
            cnm_result.id,
            cnm_result.uuid,
            cnm_result.matched_pfsp,
            cnm_result.matched_pfsp AS matched_pfsp_id,
            cnm_result.cnm_folder AS target_uuid,
            cnm_result.target_type as flag_type,
            tmp.uuid AS file_uuid,
            tmp.filetype_name
        
        FROM cnm_result
        
        LEFT JOIN (
            SELECT DISTINCT ON ( cnm_result )
                cnm_candidate.uuid,
                cnm_candidate.cnm_result,
                cnm_candidate_filetype.name AS filetype_name
            FROM cnm_candidate
            LEFT JOIN cnm_candidate_filetype ON cnm_candidate.file_type = cnm_candidate_filetype.id
            ORDER BY cnm_candidate.cnm_result, cnm_candidate.file_type ASC
        ) AS tmp ON cnm_result.uuid = tmp.cnm_result
        
        WHERE
            tmp.uuid IS NOT NULL
        
        ORDER BY
            cnm_result.id DESC
    """
    candidate_list = config.db.query_fetchall( sql )
    
    for _, candidate in enumerate( candidate_list ):
        
        try:
            current_pfsp_id = candidate.get( "matched_pfsp", "" )
            current_pfsp_id = current_pfsp_id.split( "," )[ 0 ]
            current_pfsp_id = current_pfsp_id.split( "-" )[ 0 ]
            current_pfsp_id = current_pfsp_id.replace( "F", "" )
            current_pfsp_id = int( current_pfsp_id )
            candidate[ "matched_pfsp_id" ] = current_pfsp_id
            
        except:
            candidate[ "matched_pfsp_id" ] = 0
    
    return utils.template.my_render_template(
        "afis/admin/list_all_candidates.html",
        candidate_list = candidate_list,
    )

@afis_view.route( "/afis/<cnm_uuid>/<file_uuid>/<fpc>/autodetect" )
@afis_view.route( "/afis/<cnm_uuid>/<file_uuid>/autodetect" )
@utils.decorator.login_required
def image_auto_detect_format( cnm_uuid, file_uuid, fpc = 0 ):
    try:
        img = views.nist.cnm_candidate_get_image( cnm_uuid, file_uuid, fpc )
        
    except:
        try:
            sql = """
                SELECT data
                FROM cnm_candidate
                WHERE
                    cnm_result = %s AND
                    uuid = %s
            """
            data = config.db.query_fetchone( sql, ( cnm_uuid, file_uuid, ) )[ "data" ]
            img = views.images.str2img( data )
            
        except:
            img = no_preview_image( return_pil = True )
    
    img = utils.images.patch_image_to_web_standard( img )
    
    img.thumbnail( ( 800, 800 ) )
    buff = utils.images.pil2buffer( img, "JPEG" )
    return send_file( buff, mimetype = "image/jpeg" )

@afis_view.route( "/afis/<cnm_uuid>/<file_uuid>/<fpc>/autodetect/tiff" )
@afis_view.route( "/afis/<cnm_uuid>/<file_uuid>/autodetect/tiff" )
@utils.decorator.login_required
def image_auto_detect_format_raw( cnm_uuid, file_uuid, fpc = 0 ):
    try:
        img = views.nist.cnm_candidate_get_image( cnm_uuid, file_uuid, fpc )
        
    except:
        try:
            sql = """
                SELECT data
                FROM cnm_candidate
                WHERE
                    cnm_result = %s AND
                    uuid = %s
            """
            data = config.db.query_fetchone( sql, ( cnm_uuid, file_uuid, ) )[ "data" ]
            img = views.images.str2img( data )
            
        except:
            img = no_preview_image( return_pil = True )
    
    img = utils.images.patch_image_to_web_standard( img )
    
    # Image resampling to 1000dpi
    try:
        res, _ = img.info[ 'dpi' ]
    except:
        current_app.logger.debug("KEYERROR with DPI result, manually inserting dpi (500 , 500)")
        img.info['dpi'] = (500, 500)
        res, _ = img.info[ 'dpi' ]
    current_app.logger.debug("DPI: " + str(img.info['dpi']))
    if res != 1000:
        fac = 1000 / float( res )
        w, h = img.size
        img = img.resize( ( int( w * fac ), int( h * fac ) ), Image.BICUBIC )
        img.info[ 'dpi' ] = ( 1000, 1000 )
    
    # Return the image
    buff = utils.images.pil2buffer( img, "TIFF" )
    return send_file(
        buff,
        mimetype = "image/tiff",
        as_attachment = True,
        attachment_filename = "{}.tiff".format( file_uuid, )
    )

@afis_view.route( "/afis/<cnm_uuid>/<file_uuid>/<fpc>/res" )
@afis_view.route( "/afis/<cnm_uuid>/<file_uuid>/res" )
@utils.decorator.login_required
def nist_get_resolution( cnm_uuid, file_uuid, fpc = 0 ):
    res, width, height = views.nist.nist_get_image_resolution( cnm_uuid, file_uuid, fpc )
    
    return jsonify( {
        "res": res,
        "width": width,
        "height": height
    } )
    
