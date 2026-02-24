#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import jsonify, session, redirect, url_for, abort

import config
import utils
import views
import views.uuid.functions

uuid_view = Blueprint( "uuid", __name__, template_folder = "templates" )

@uuid_view.route( "/uuid/get_table/<uuid>" )
@utils.decorator.admin_required
def get_table_for_uuid_route( uuid ):
    try:
        table = views.uuid.functions.get_table_for_uuid( uuid )
        
        return jsonify( {
            "error": False,
            "table": table
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@uuid_view.route( "/uuid" )
@utils.decorator.login_required
def search_page():
    lst = views.uuid.functions.get_all_uuid_partial()
    return jsonify( lst )

@uuid_view.route( "/uuid/search" )
@utils.decorator.login_required
def search_uuid():
    lst = views.uuid.functions.get_all_uuid_partial()
    return utils.template.my_render_template(
        "uuid/search.html",
        uuid_list = lst
    )

@uuid_view.route( "/uuid/autoopen/<uuid>" )
@utils.decorator.login_required
def autoopen( uuid ):
    lst = []
    for cuuid, table in views.uuid.functions.get_all_uuid().iteritems():
        if uuid in cuuid[ 0:18 ]:
            lst.append( {
                "table": table,
                "uuid": cuuid
            } )
    
    if len( lst ) != 1:
        return jsonify( lst )
    else:
        target = lst[ 0 ]
        
        if session[ "account_type_name" ] == "Administrator":
            if target[ "table" ] == "submissions":
                return redirect( url_for( "submission.admin_submission_home", submission_id = target[ "uuid" ] ) )

            elif target[ "table" ] == "files":
                file_type = type_of_file( target[ "uuid" ] )
                if file_type in [ "tenprint_card_front", "tenprint_card_back" ]:
                    return redirect( url_for( "submission.admin_tenprint", submission_id = views.images.get_submission_uuid_for_file( target[ "uuid" ] ), tenprint_id = target[ "uuid" ] ) )
                elif file_type in [ "mark_target", "mark_incidental" ]:
                    return redirect( url_for( "submission.admin_submission_mark", submission_id = views.images.get_submission_uuid_for_file( target[ "uuid" ] ), mark_id = target[ "uuid" ] ) )

            elif target[ "table" ] == "cnm_folder":
                return redirect( url_for( "afis.admin_show_target", uuid = target[ "uuid" ] ) )

            elif target[ "table" ] == "cnm_annotation":
                cnm_folder, fpc = cnm_folder_of_annotation( target[ "uuid" ] )
                return redirect( url_for( "afis.admin_view_segment", folder_id = cnm_folder, fpc = fpc ) )
            
            elif target[ "table" ] == "cnm_annotation":
                sql = "SELECT folder_uuid FROM cnm_annotation WHERE uuid = %s"
                folder_uuid = config.db.query_fetchone( sql, ( target[ "uuid" ], ) )[ "folder_uuid" ]
                return redirect( url_for( "afis.admin_show_target", uuid = folder_uuid ) )
            
            elif target[ "table" ] == "files_segments":
                sql = """
                    SELECT
                        submissions.uuid,
                        files_segments.tenprint,
                        files_segments.pc
                    FROM files_segments
                    LEFT JOIN files ON files_segments.tenprint = files.uuid
                    LEFT JOIN submissions ON files.folder = submissions.id
                    WHERE files_segments.uuid = %s
                """
                submission_id, tenprint_id, pc = config.db.query_fetchone( sql, ( target[ "uuid" ], ) )
                
                return redirect( url_for( "submission.submission_segment", submission_id = submission_id, tenprint_id = tenprint_id, pc = pc ) )
            
            elif target[ "table" ] == "cnm_result":
                sql = """
                    SELECT
                        cnm_result.uuid,
                        cnm_result.cnm_folder AS target_uuid
                    FROM cnm_result
                    WHERE cnm_result.uuid = %s
                """
                cnm_uuid, target_uuid = config.db.query_fetchone( sql, ( target[ "uuid" ], ) )
                return redirect( url_for( "afis.admin_cnm_edit", target_uuid = target_uuid, cnm_uuid = cnm_uuid ) )
            
            elif target[ "table" ] == "cnm_candidate":
                sql = """
                    SELECT
                        cnm_result.uuid,
                        cnm_result.cnm_folder AS target_uuid,
                        cnm_candidate.uuid AS file_uuid,
                        cnm_candidate_filetype.name AS filetype_name
                    FROM cnm_candidate
                    LEFT JOIN cnm_result ON cnm_candidate.cnm_result = cnm_result.uuid
                    LEFT JOIN cnm_candidate_filetype ON cnm_candidate.file_type = cnm_candidate_filetype.id
                    WHERE
                        cnm_candidate.uuid = %s
                """
                cnm_uuid, target_uuid, file_uuid, filetype_name = config.db.query_fetchone( sql, ( target[ "uuid" ], ) )
                
                if filetype_name == "card":
                    return redirect( url_for( "afis.admin_cnm_view_nist_file", target_uuid = target_uuid, cnm_uuid = cnm_uuid, file_uuid = file_uuid ) )
                else:
                    return redirect( url_for( "afis.admin_cnm_edit", target_uuid = target_uuid, cnm_uuid = cnm_uuid ) )
        
        else:
            if target[ "table" ] == "submissions":
                return redirect( url_for( "submission.submission_upload_tenprintmark", submission_id = target[ "uuid" ] ) )
            
            elif target[ "table" ] == "files":
                file_type = type_of_file( target[ "uuid" ] )
                if file_type in [ "tenprint_card_front", "tenprint_card_back" ]:
                    return redirect( url_for( "submission.submission_tenprint", submission_id = views.images.get_submission_uuid_for_file( target[ "uuid" ] ), tenprint_id = target[ "uuid" ] ) )
                elif file_type in [ "mark_target", "mark_incidental" ]:
                    return redirect( url_for( "submission.submission_mark", submission_id = views.images.get_submission_uuid_for_file( target[ "uuid" ] ), mark_id = target[ "uuid" ] ) )

            elif target[ "table" ] == "cnm_folder":
                return redirect( url_for( "afis.show_folder", uuid = target[ "uuid" ] ) )
            
            elif target[ "table" ] == "cnm_annotation":
                cnm_folder, fpc = cnm_folder_of_annotation( target[ "uuid" ] )
                return redirect( url_for( "afis.view_segment", folder_id = cnm_folder, fpc = fpc ) )
            
            elif target[ "table" ] == "cnm_annotation":
                sql = "SELECT folder_uuid FROM cnm_annotation WHERE uuid = %s"
                folder_uuid = config.db.query_fetchone( sql, ( target[ "uuid" ], ) )[ "folder_uuid" ]
                return redirect( url_for( "afis.show_folder", uuid = folder_uuid ) )
            
            else:
                if session[ "account_type_name" ] == "AFIS":
                    if target[ "table" ] == "files_segments":
                        sql = """
                            SELECT cnm_folder.uuid
                            FROM donor_segments_v
                            LEFT join cnm_folder ON
                                donor_segments_v.donor_id = cnm_folder.donor_id AND
                                donor_segments_v.pc = cnm_folder.pc
                            WHERE donor_segments_v.uuid = %s
                        """
                        uuid = config.db.query_fetchone( sql, ( target[ "uuid" ], ) )[ "uuid" ]
                        
                        return redirect( url_for( "afis.show_folder", uuid = uuid ) )
        
        return abort( 404 )
            
def type_of_file( uuid ):
    sql = """
        SELECT
            files_type.name
        FROM files
        INNER JOIN files_type ON files.type = files_type.id
        WHERE files.uuid = %s
    """
    return config.db.query_fetchone( sql, ( uuid, ) )[ "name" ]

def cnm_folder_of_annotation( uuid ):
    sql = """
        SELECT
            folder, fpc
        FROM cnm_annotation
        WHERE uuid = %s
    """
    return config.db.query_fetchone( sql, ( uuid, ) )

