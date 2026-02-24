#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from uuid import uuid4
import json

from flask import Blueprint
from flask import session, request, jsonify, current_app

import config

from const import pfsp, pfsp2fpc, pfspdesc, pfsp_fpc_search

import utils

from MDmisc.RecursiveDefaultDict import edefaultdict, defDict

trainer_view = Blueprint( "trainer", __name__, template_folder = "templates" )

@trainer_view.route( "/marks/search" )
@utils.decorator.trainer_has_access
def search():
    """
        Provide the search page.
    """
    sql = """
        SELECT
            files.id,
            files.uuid,
            mark_info.pfsp,
            mark_info.detection_technic,
            mark_info.surface,
            files.note,
            submissions.uuid AS submission_uuid,
            users.username,
            users.id AS userid
        
        FROM files
        LEFT JOIN mark_info ON mark_info.uuid = files.uuid
        LEFT JOIN submissions ON files.folder = submissions.id
        LEFT JOIN users ON submissions.donor_id = users.id
        WHERE ( files.type = 3 OR files.type = 4 )
        ORDER BY files.id ASC
    """
    marks = config.db.query_fetchall( sql )
    
    sql = """
        SELECT
            submissions.uuid AS submissions_uuid,
            segments_locations.fpc,
            segments_locations.tenprint_id
        
        FROM segments_locations
        INNER JOIN files ON segments_locations.tenprint_id = files.uuid
        LEFT JOIN submissions ON files.folder = submissions.id
        ORDER BY fpc
    """
    ref_list = config.db.query_fetchall( sql )
    refs = defDict()
    for ref in ref_list:
        refs[ ref[ "submissions_uuid" ] ][ ref[ "fpc" ] ] = ref[ "tenprint_id" ]

    sql = """
        SELECT
            donor_fingers_gp.donor_id AS id,
            donor_fingers_gp.fpc,
            gp.name
        FROM donor_fingers_gp
        LEFT JOIN gp ON donor_fingers_gp.gp = gp.id
    """
    donors_gp = config.db.query_fetchall( sql )
    
    all_detection_technics = config.db.query_fetchall( "SELECT * FROM detection_technics ORDER BY name ASC" )
    surfaces = config.db.query_fetchall( "SELECT * FROM surfaces ORDER BY name ASC" )
    
    for _, v in enumerate( marks ):
        for col in [ "detection_technic", "surface", "note" ]:
            for old, new in [ ( "{", "" ), ( "}", "" ), ( "\n", "; " ) ]:
                try:
                    v[ col ] = v[ col ].replace( old, new )
                except:
                    pass
        
        v[ "username" ] = v[ "username" ].replace( "_", " " )

    # Current working folder
    current_exercise_folder = session.get( "current_exercise_folder", "" )
    sql = "SELECT * FROM exercises WHERE trainer_id = %s ORDER BY name ASC"
    all_exercises_list = config.db.query_fetchall( sql, ( session[ "user_id" ], ) )

    #
    return utils.template.my_render_template(
        "trainer/search.html",
        marks = marks,
        refs = refs,
        donors_gp = donors_gp,
        current_exercise_folder = current_exercise_folder,
        all_exercises_list = all_exercises_list,
        pfsp2fpc = pfsp2fpc,
        pfspdesc = pfspdesc,
        pfsp_fpc_search = pfsp_fpc_search,
        all_detection_technics = all_detection_technics,
        surfaces = surfaces,
        all_pfsp = pfsp.zones
    )

@trainer_view.route( "/exercises/list" )
@utils.decorator.trainer_has_access
def exercises_list():
    if session[ "account_type_name" ] == "Administrator":
        sql = """
            SELECT
                exercises.*,
                users.username
            FROM exercises
            LEFT JOIN users ON exercises.trainer_id = users.id
            ORDER BY name ASC
        """
        data = ()
    
    else:
        sql = """
            SELECT *
            FROM exercises
            WHERE
                trainer_id = %s AND
                active = true
            ORDER BY name ASC
        """
        data = ( session[ "user_id" ], )
    
    ex_list = config.db.query_fetchall( sql, data )
    
    marks_count = {}
    sql = """
        SELECT
            folder AS uuid,
            count( * ) AS nb
        FROM exercises_folder
        GROUP BY folder
    """
    for c in config.db.query_fetchall( sql ):
        marks_count[ c[ "uuid" ] ] = c[ "nb" ]

    return utils.template.my_render_template(
        "trainer/exercises.html",
        ex_list = ex_list,
        marks_count = marks_count
    )

@trainer_view.route( "/exercises/new", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def exercises_new():
    try:
        name = request.form.get( "name" )
        uuid = str( uuid4() )
        trainer_id = session[ "user_id" ]

        sql = utils.sql.sql_insert_generate( "exercises", [ "name", "uuid", "trainer_id" ], "id" )
        config.db.query_fetchone( sql, ( name, uuid, trainer_id, ) )

        return jsonify( {
            "error": False,
            "data": uuid
        } )
    
    except:
        return jsonify( {
            "error": True,
            "msg": "Error while creating the exercises list"
        } )

@trainer_view.route( "/exercises/rename", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def exercises_rename():
    try:
        new_name = request.form.get( "name" )
        uuid = request.form.get( "uuid" )
        
        sql = "UPDATE exercises SET name = %s WHERE uuid = %s AND trainer_id = %s"
        config.db.query( sql, ( new_name, uuid, session[ "user_id" ], ) )
        
        return jsonify( {
            "error": False
        } )

    except:
        return jsonify( {
            "error": True
        } )

@trainer_view.route( "/exercises/add_to_list", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def add_mark_to_list():
    try:
        folder = request.form.get( "folder", False )
    except:
        try:
            sql = "SELECT uuid FROM exercises WHERE trainer_id = %s ORDER BY creationtime"
            folder = config.db.query_fetchone( sql, ( session[ "user_id" ], ) )[ "uuid" ]
        except:
            sql = utils.sql.sql_insert_generate( "exercises", [ "uuid", "trainer_id", "name" ], "uuid" )
            data = ( str( uuid4() ), session[ "user_id" ], "no name", )
            folder = config.db.query_fetchone( sql, data )[ "uuid" ]

    try:
        mark = request.form.get( "mark", False )
        current_app.logger.info( "Add {} to {}".format( mark, folder ) )
        
        sql = "SELECT count(*) FROM exercises_folder WHERE mark = %s AND folder = %s"
        c = config.db.query_fetchone( sql, ( mark, folder, ) )[ "count" ]
        if c == 0:
            sql = utils.sql.sql_insert_generate( "exercises_folder", [ "mark", "folder" ], "id" )
            config.db.query_fetchone( sql, ( mark, folder, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@trainer_view.route( "/exercises/add_exemplar_to_list", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def add_exemplar_to_list():
    try:
        folder = request.form.get( "folder", False )
    except:
        try:
            sql = "SELECT uuid FROM exercises WHERE trainer_id = %s ORDER BY creationtime"
            folder = config.db.query_fetchone( sql, ( session[ "user_id" ], ) )[ "uuid" ]
        except:
            sql = utils.sql.sql_insert_generate( "exercises", [ "uuid", "trainer_id", "name" ], "uuid" )
            data = ( str( uuid4() ), session[ "user_id" ], "no name", )
            folder = config.db.query_fetchone( sql, data )[ "uuid" ]

    try:
        mark = request.form.get( "mark", False )
        current_app.logger.info( "Add {} to {}".format( mark, folder ) )
        
        sql = "SELECT count(*) FROM exercises_folder WHERE mark = %s AND folder = %s"
        c = config.db.query_fetchone( sql, ( mark, folder, ) )[ "count" ]
        if c == 0:
            sql = utils.sql.sql_insert_generate( "exercises_folder", [ "mark", "folder" ], "id" )
            config.db.query_fetchone( sql, ( mark, folder, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@trainer_view.route( "/exercises/remove_from_list", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def remove_mark_from_list():
    try:
        mark = request.form.get( "mark", False )
        folder_id = request.form.get( "folder_id", False )
        
        sql = "DELETE FROM exercises_folder WHERE mark = %s AND folder = %s"
        config.db.query( sql, ( mark, folder_id, ) )

        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@trainer_view.route( "/exercises/<folder_id>/show" )
@utils.decorator.trainer_has_access
def show_folder_content( folder_id ):
    sql = """
        SELECT files_v.*
        FROM files_v
        INNER JOIN exercises_folder ON exercises_folder.mark = files_v.uuid
        WHERE exercises_folder.folder = %s
        ORDER BY id ASC
    """
    mark_list = config.db.query_fetchall( sql, ( folder_id, ) )
    
    sql = "SELECT name FROM exercises WHERE uuid = %s"
    folder_name = config.db.query_fetchone( sql, ( folder_id, ) )[ "name" ]

    return utils.template.my_render_template(
        "trainer/folder_show.html",
        folder = folder_id,
        folder_name = folder_name,
        mark_list = mark_list
    )


@trainer_view.route( "/exercises/<folder_id>/trainee" )
@utils.decorator.trainer_has_access
def show_folder_trainee( folder_id ):
    sql = "SELECT name FROM exercises WHERE uuid = %s"
    folder_name = config.db.query_fetchone( sql, ( folder_id, ) )[ "name" ]
    
    sql = """
        SELECT *
        FROM users
        INNER JOIN exercises_trainee_list ON users.id = exercises_trainee_list.user_id
        WHERE
            exercises_trainee_list.folder = %s AND
            users.type = 7
    """
    trainee_list = config.db.query_fetchall( sql, ( folder_id, ) )
    
    return utils.template.my_render_template(
        "trainer/trainee.html",
        folder = folder_id,
        folder_name = folder_name,
        trainee_list = trainee_list
    )

@trainer_view.route( "/exercises/<folder_id>/trainee/add", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def add_users_to_folder( folder_id ):
    try:
        users_email_list = request.form.get( "users", None )
        users_email_list = users_email_list.replace( "\n", ";" ).split( ";" )

        for user_email in users_email_list:
            current_app.logger.debug("current email: " + str(user_email))
            if user_email == "":
                continue
            
            try:
                sql = """
                    SELECT count( email ) AS nb
                    FROM users
                    LEFT JOIN exercises_trainee_list ON users.id = exercises_trainee_list.user_id
                    WHERE
                        exercises_trainee_list.folder = %s AND
                        email = %s
                    GROUP BY email
                """
                nb = config.db.query_fetchone( sql, ( folder_id, user_email, ) )[ "nb" ]
            except TypeError:
                current_app.logger.debug("ADD USERS nb value is 0! TypeError exception GOOD")
                nb = 0
            
            if nb == 0:
                userid = config.db.query_fetchone( "SELECT nextval( 'username_trainee_seq' ) as id" )[ "id" ]
                current_app.logger.debug("userid: " + str(userid))
                username = "trainee_{}".format( userid )
                
                sql = utils.sql.sql_insert_generate( "users", [ "username", "email", "type" ], "id" )
                data = ( username, user_email, 7 )
                trainee_user_id = config.db.query_fetchone( sql, data )[ "id" ]
                
                sql = utils.sql.sql_insert_generate( "exercises_trainee_list", [ "user_id", "folder" ], "id" )
                data = ( trainee_user_id, folder_id, )
                config.db.query_fetchone( sql, data )

            else:
                continue


        return jsonify( {
            "error": False
        } )

    except:
        return jsonify( {
            "error": True
        } )

@trainer_view.route( "/exercises/<folder_id>/trainee/remove", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def remove_user_from_folder( folder_id ):
    user_id = request.form.get( "user_id", None )
    try:
        sql = "DELETE FROM exercises_trainee_list WHERE user_id = %s AND folder = %s"
        config.db.query( sql, ( user_id, folder_id, ) )

        return jsonify( {
            "error": False,
        } )

    except:
        return jsonify( {
            "error": True
        } )

@trainer_view.route( "/exercises/get/current_folder_id" )
@utils.decorator.trainer_has_access
def get_current_folder_id():
    folder = session.get( "current_exercise_folder", None )
    return jsonify( {
        "error": False,
        "folder_id": folder
    } )

@trainer_view.route( "/exercises/set/current_folder_id", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def set_current_folder_id():
    folder = request.form.get( "current_folder_id", None )
    if folder != None:
        session[ "current_exercise_folder" ] = folder
    
    return jsonify( {
        "error": False,
    } )
@trainer_view.route( "/exercises/add_tenprint", methods = [ "POST" ] )
@utils.decorator.trainer_has_access
def add_tenprint_to_exercise():
    sql = """
        SELECT
            files.id, files.uuid,
            files.folder,
            users.username,
            submissions.uuid as submission_uuid
        FROM files
        LEFT JOIN submissions ON files.folder = submissions.id
        LEFT JOIN users ON submissions.donor_id = users.id
        WHERE
            ( files.type = 1 OR files.type = 2 ) AND
            submissions.uuid = %s AND
            users.username IS NOT NULL
        ORDER BY users.id ASC, files.type, files.id ASC
    """
    submission_uuid = request.form.get( "uuid", False )
    data = ( submission_uuid, )
    
    tenprint_cards = config.db.query_fetchall( sql, data )
    try:
        folder = request.form.get( "folder", False )
    except:
        try:
            sql = "SELECT uuid FROM exercises WHERE trainer_id = %s ORDER BY creationtime"
            folder = config.db.query_fetchone( sql, ( session[ "user_id" ], ) )[ "uuid" ]
        except:
            sql = utils.sql.sql_insert_generate( "exercises", [ "uuid", "trainer_id", "name" ], "uuid" )
            data = ( str( uuid4() ), session[ "user_id" ], "no name", )
            folder = config.db.query_fetchone( sql, data )[ "uuid" ]

    try:
        for mark in tenprint_cards:
            current_app.logger.info("MARK  is " + str(mark[1]))
            mark = mark[1]
            current_app.logger.info( "Add MARK {} to {}".format( mark, folder ) )

            sql = "SELECT count(*) FROM exercises_folder WHERE mark = %s AND folder = %s"
            c = config.db.query_fetchone( sql, ( mark, folder, ) )[ "count" ]
            current_app.logger.debug("MARK VALUE of c is: " + str(c))
            if c == 0:
                sql = utils.sql.sql_insert_generate( "exercises_folder", [ "mark", "folder" ], "id" )
                current_app.logger.debug("MARK ADDED " + str(mark[1]) + " to folder")
                config.db.query_fetchone( sql, ( mark, folder, ) )
            else:
                current_app.logger.debug("MARK moving to next one")
        return jsonify( {
            "error": False
        } )
        
    except Exception as e:
        current_app.logger.debug("MARK ERROR FOUND: " + str(e))
        return jsonify( {
            "error": True
        } )


def get_cnm_list_files( cnm_uuid, file_type ):
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