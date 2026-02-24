#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import current_app, jsonify

from PIL import Image

from PiAnoS import caseExistsInDB

import views

import config
import utils

pianos_view = Blueprint( "pianos", __name__, template_folder = "templates" )

@pianos_view.route( "/pianos_api" )
@utils.decorator.admin_required
def pianos_actions():
    """
        Serve the page with all actions related to the dedicated PiAnoS server.
    """
    current_app.logger.info( "Serve the PiAnoS actions page" )
    
    return utils.template.my_render_template( "PiAnoS/actions.html" )

@pianos_view.route( "/pianos_api/add_user/all" )
@utils.decorator.admin_required
def pianos_update_all_accounts():
    """
        serve the function to update the users in PiAnoS
    """
    current_app.logger.info( "Copy all accounts to PiAnoS" )
    
    return jsonify( {
        "error": not do_pianos_update_all_accounts()
    } )

def do_pianos_update_all_accounts():
    """
        Copy/update the credentials for all users.
        This function keep the credentials in sync between ICNML and PiAnoS.
    """
    try:
        sql = """
            SELECT users.username, users.password, account_type.name as g
            FROM users
            LEFT JOIN account_type ON users.type = account_type.id
            WHERE users.password IS NOT NULL
        """
        nb = 0
        for user in config.db.query_fetchall( sql ):
            nb += 1
            username, h, group_name = user
            
            current_app.logger.debug( "Copy the user '{}' to PiAnoS".format( username ) )
            
            groupid = config.pianosdb.create_group( group_name )
            pianos_user_id = config.pianosdb.create_user( username = username, hash = h, groupid = groupid )
            config.pianosdb.reset_user( username, hash = h )
            config.pianosdb.create_folder( "{}'s folder".format( username ), pianos_user_id, None, pianos_user_id )
        
        config.pianosdb.commit()
        
        current_app.logger.info( "{} users copied to PiAnoS".format( nb ) )
        
        return True
    
    except:
        return False

@pianos_view.route( "/pianos_api/add_segments/all" )
@utils.decorator.admin_required
def pianos_copy_all_segments():
    """
        Route to push all segments to PiAnoS.
    """
    current_app.logger.info( "Copy all segments to PiAnoS" )
    
    return jsonify( {
        "error": not do_pianos_copy_all_segments()
    } )

def do_pianos_copy_all_segments():
    """
        Copy all segments images to PiAnoS. If the case already exists, the image is not pushed to PiAnoS.
    """
    try:
        img = Image.new( "L", ( 200, 200 ), 255 )
        empty_img_res = 500
        empty_img_id = config.pianosdb.create_image( "PRINT", img, empty_img_res, "empty" )
        
        sql = """
            SELECT
                files_segments.uuid,
                files_segments.data,
                files_segments.pc,
                files_v.resolution,
                submissions.id as submissionid,
                submissions.uuid as submissionuuid
            FROM files_segments
            LEFT JOIN files_v ON files_segments.tenprint = files_v.uuid
            LEFT JOIN submissions ON files_v.folder = submissions.id
        """
        for segment in config.db.query_fetchall( sql ):
            data = utils.encryption.do_decrypt_dek( segment[ "data" ], segment[ "submissionuuid" ] )
            img = views.images.str2img( data )
            
            current_app.logger.debug( "{}: {}".format( segment[ "uuid" ], img ) )
            
            try:
                folder_id = config.pianosdb.create_folder( "submission {}".format( segment[ "submissionid" ] ) )
                case_name = "submission {} segment {}".format( segment[ "submissionid" ], segment[ "pc" ] )
                
                config.pianosdb.create_exercise( 
                    folder_id,
                    case_name, "",
                    img, segment[ "resolution" ],
                    empty_img_id, empty_img_res
                )
            except caseExistsInDB:
                continue
            except:
                raise Exception( "case exists in db" )
        
            config.pianosdb.commit()
    
        return True
    
    except:
        return False
