#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import current_app
from flask import request, session, jsonify

import json

import config

import utils

donor_view = Blueprint( "donor", __name__, template_folder = "templates" )

@donor_view.route( "/dek/reconstruct", methods = [ "POST" ] )
@utils.decorator.login_required
def dek_regenerate():
    """
        Regenerate the Data Encryption Key for a particular donor.
        
        This function takes in hash of the email of the donor as input to
        compute the DEK. This requires the presence of the salt in the
        database. If the DEK is recmputed correctly (checked against the
        `dek_check` variables stored in the database), the value is stored in
        the database.
    """
    current_app.logger.info( "DEK reconstruction" )
    try:
        # Extract the input from the input form
        email_hash = request.form.get( "email_hash" )
        username = session.get( "username" )
        
        current_app.logger.debug( "User: {}".format( username ) )
        
        # Retrieve the information already present in the database (salt and dek_check)
        sql = "SELECT * FROM donor_dek WHERE donor_name = %s"
        user = config.db.query_fetchone( sql, ( username, ) )
        
        if user[ "salt" ] == None:
            current_app.logger.error( "No DEK salt for user '{}'".format( session[ "username" ] ) )
            raise Exception( "no DEK" )
        
        # Recompute the DEK with the hash of the email and the salt
        _, dek, _ = utils.encryption.dek_generate( username = username, email_hash = email_hash, salt = user[ "salt" ] )
        
        current_app.logger.debug( "DEK reconstructed: {}...".format( dek[ 0:10 ] ) )
        
        # Check the integrity of the reconstructed DEK
        check = utils.aes.do_decrypt( user[ "dek_check" ], dek )
        check = json.loads( check )
        
        if check[ "value" ] != "ok":
            current_app.logger.error( "DEK check error for user '{}'".format( session[ "username" ] ) )
            raise Exception( "DEK check error" )
        
        current_app.logger.debug( "DEK check OK" )
        
        # Save the DEK to the database
        sql = "UPDATE donor_dek SET dek = %s WHERE id = %s AND donor_name = %s"
        config.db.query( sql, ( dek, user[ "id" ], username, ) )
        
        current_app.logger.info( "Reconstructed DEK saved to the database" )
        
        # Return OK
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@donor_view.route( "/dek/delete" )
@utils.decorator.login_required
def dek_delete():
    """
        Delete the Data Encryption Key related to the current logged-in user.
        The selection of the correct user to delete the DEK is done
        automatically based upon the current session id.
        
        This is only used for silent deletion of the DEK (this function deletes
        only the `dek` column). The DEK can still be recomputed by the donor or
        the submitter.
    """
    try:
        username = session.get( "username" )
        
        current_app.logger.info( "Delete DEK for user {}".format( username ) )
        
        sql = "UPDATE donor_dek SET dek = NULL WHERE donor_name = %s"
        config.db.query( sql, ( username, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@donor_view.route( "/dek/fulldelete" )
@utils.decorator.login_required
def dek_delete_fully():
    """
        Fully delete the Data Encryption Key and the salt for the logged-in
        user. This function is used when the donor wants to delete himself
        completly. This function will also delete the random salt related to
        the donor. It's not possible to recopute the DEK if this function is
        used.
    """
    try:
        username = session.get( "username" )
        
        current_app.logger.info( "Fully delete the DEK of user {}".format( username ) )
        
        sql = "UPDATE donor_dek SET dek = NULL WHERE donor_name = %s"
        config.db.query( sql, ( username, ) )
        sql = "UPDATE donor_dek SET salt = NULL WHERE donor_name = %s"
        config.db.query( sql, ( username, ) )
        sql = "UPDATE donor_dek SET dek_check = NULL WHERE donor_name = %s"
        config.db.query( sql, ( username, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@donor_view.route( "/user/myprofile/dek" )
@utils.decorator.login_required
def user_myprofile_dek():
    """
        Serve the page to manage the Data Encryption Key of a donor.
    """
    current_app.logger.info( "Serve the donor DEK page" )
    
    sql = """
        SELECT dek, salt
        FROM donor_dek
        WHERE donor_name = %s
    """
    data = config.db.query_fetchone( sql, ( session[ "username" ], ) )
    
    has_dek = data[ "dek" ] != None
    has_salt = data[ "salt" ] != None
    
    current_app.logger.debug( "username: {}".format( session[ "username" ] ) )
    current_app.logger.debug( "has_dek:  {}".format( has_dek ) )
    current_app.logger.debug( "has_salt: {}".format( has_salt ) )
    
    return utils.template.my_render_template( 
        "donor/dek.html",
        has_dek = has_dek,
        has_salt = has_salt
    )

@donor_view.route( "/user/myprofile/tenprint" )
@utils.decorator.login_required
def user_myprofile_tenprint():
    """
        This page will display the tenprint cards associated with the current user.
    """
    current_app.logger.info( "Serve the page with all tenprint to the donor" )
    
    sql = """
        SELECT
            files.id,
            files.uuid
        FROM users
        LEFT JOIN submissions ON users.id = submissions.donor_id
        LEFT JOIN files ON files.folder = submissions.id
        LEFT JOIN files_type ON files.type = files_type.id
        WHERE
            users.id = %s AND
            (
                files_type.name = 'tenprint_card_front' OR
                files_type.name = 'tenprint_card_back' OR
                files_type.name = 'tenprint_nist'
            )
    """
    tenprint_cards = config.db.query_fetchall( sql, ( session[ "user_id" ], ) )
    nb_tenprint = len( tenprint_cards )
    
    current_app.logger.debug( "{} tenprint(s) stored in database".format( len( tenprint_cards ) ) )
    
    return utils.template.my_render_template( 
        "donor/tenprint.html",
        tenprint_cards = tenprint_cards,
        nb_tenprint = nb_tenprint
    )

@donor_view.route( "/user/myprofile/marks" )
@utils.decorator.login_required
def user_myprofile_marks():
    """
        This page will display the marks associated with the current user.
    """
    current_app.logger.info( "Serve the page with all marks to the donor" )
    
    sql = """
        SELECT files.id, files.uuid
        FROM users
        LEFT JOIN submissions ON users.id = submissions.donor_id
        LEFT JOIN files ON files.folder = submissions.id
        LEFT JOIN files_type ON files.type = files_type.id
        WHERE
            users.id = %s AND
            (
                files_type.name = 'mark_target' OR
                files_type.name = 'mark_incidental'
            )
    """
    marks = config.db.query_fetchall( sql, ( session[ "user_id" ], ) )
    nb_marks = len( marks )
    
    current_app.logger.debug( "{} mark(s) stored in database".format( len( marks ) ) )
    
    return utils.template.my_render_template(
        "donor/marks.html",
        marks = marks,
        nb_marks = nb_marks
    )

