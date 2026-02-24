#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from email.mime.text import MIMEText
from uuid import uuid4
import base64
import hashlib
import json

from flask import Blueprint
from flask import current_app, request, jsonify, session, url_for, redirect
import webauthn

import config

import views

import utils

newuser_view = Blueprint( "newuser", __name__, template_folder = "templates" )

@newuser_view.route( "/signin" )
def new_user():
    """
        Serve the page to register to ICNML.
    """
    current_app.logger.info( "New user registration page open" )
    
    account_type = config.db.query_fetchall( "SELECT id, name FROM account_type WHERE can_singin = true" )
    
    return utils.template.my_render_template(
        "newuser/signin.html",
        list_account_type = account_type
    )

@newuser_view.route( "/do/signin", methods = [ "POST" ] )
def add_account_request_to_db():
    """
        Add the new user request to the database.
    """
    current_app.logger.info( "Registrer new user request to the database" )
    
    try:
        first_name = request.form[ "first_name" ]
        last_name = request.form[ "last_name" ]
        email = request.form[ "email" ]
        account_type = int( request.form[ "account_type" ] )
        uuid = str( uuid4() )
        
        email = email.lower()
        
        current_app.logger.debug( "First name: {}".format( first_name ) )
        current_app.logger.debug( "Last name:  {}".format( last_name ) )
        current_app.logger.debug( "Email:      {}".format( email ) )
        current_app.logger.debug( "Account:    {}".format( account_type ) )
        
        sql = "SELECT name FROM account_type WHERE id = %s"
        account_type_name = config.db.query_fetchone( sql, ( account_type, ) )[ "name" ]
        account_type_name = account_type_name.lower()

        sql = "SELECT nextval( 'username_{}_seq' ) as id".format( account_type_name ) 
        username_id = config.db.query_fetchone( sql )[ "id" ]
        
        current_app.logger.debug( "Username id:{}".format( username_id ) )
        
        config.db.query( 
            utils.sql.sql_insert_generate( "signin_requests", [ "first_name", "last_name", "email", "account_type", "uuid", "username_id" ] ),
            ( first_name, last_name, email, account_type, uuid, username_id, )
        )
        
        return jsonify( {
            "error": False,
            "uuid": uuid
        } )
        
    except:
        current_app.logger.error( "New user request database error" )
        
        return jsonify( {
            "error": True
        } )

@newuser_view.route( "/validate_signin" )
@utils.decorator.admin_required
def validate_signin():
    """
        Serve the page to admins regarding the validation of new users.
    """
    current_app.logger.info( "Serve the signin valiation page" )
    
    sql = """
        SELECT signin_requests.*, account_type.name as account_type
        FROM signin_requests
        LEFT JOIN account_type ON signin_requests.account_type = account_type.id
        WHERE signin_requests.status = 'pending'
    """
    
    try:
        users = config.db.query_fetchall( sql )
    
    except:
        users = []
    
    return utils.template.my_render_template(
        "newuser/validate_signin.html",
        users = users
    )

@newuser_view.route( "/do/validate_signin", methods = [ "POST" ] )
@utils.decorator.admin_required
def do_validate_signin():
    """
        Prepare the new user data to be signed by the admin, and serve the page.
    """
    request_id = request.form.get( "id" )
    
    current_app.logger.info( "Signin validation begin for request_id '{}'".format( request_id ) )
    
    s = config.db.query_fetchone( "SELECT * FROM signin_requests WHERE id = %s", ( request_id, ) )
    s = dict( s )
    
    r = {}
    
    r[ "user" ] = s
    r[ "user" ][ "request_time" ] = str( r[ "user" ][ "request_time" ] )
    r[ "user" ][ "validation_time" ] = str( r[ "user" ][ "validation_time" ] )
    
    r[ "acceptance" ] = {}
    r[ "acceptance" ][ "username" ] = session[ "username" ]
    r[ "acceptance" ][ "time" ] = str( datetime.now() )
    
    j = json.dumps( r )
    challenge = base64.b64encode( j )
    challenge = challenge.replace( "=", "" )
    session[ "validation_user_challenge" ] = challenge
    
    ############################################################################
    
    user_id = session[ "user_id" ]
    
    key_list = config.db.query_fetchall( "SELECT * FROM webauthn WHERE user_id = %s AND active = true", ( user_id, ) )
    
    credential_id_list = []
    for key in key_list:
        credential_id_list.append( {
            "type": "public-key",
            "id": key[ "credential_id" ],
            "transports": [ "usb", "nfc", "ble", "internal" ]
        } )
        current_app.logger.debug( "key '{}' added to the usable keys".format( key[ "credential_id" ] ) )
    
    assertion_dict = {
        "challenge": challenge,
        "timeout": 60000,
        "allowCredentials": credential_id_list,
        "rpId": config.RP_ID,
        "userVerification": "discouraged"
    }
    
    return jsonify( {
        "error": False,
        "data": assertion_dict
    } )

@newuser_view.route( "/do/validate_signin_2", methods = [ "POST" ] )
@utils.decorator.admin_required
def do_validate_signin_2():
    """
        Verification of the signature of the new user data by the admin.
    """
    current_app.logger.info( "Verification of the validated new user" )
    
    challenge = session.get( "validation_user_challenge" )
    assertion_response = request.form
    assertion_response_s = base64.b64encode( json.dumps( assertion_response ) )
    credential_id = assertion_response.get( "id" )
    
    user = config.db.query_fetchone( "SELECT * FROM webauthn WHERE credential_id = %s", ( credential_id, ) )
    
    webauthn_user = webauthn.WebAuthnUser( 
        user[ "ukey" ], session[ "username" ], session[ "username" ], None,
        user[ "credential_id" ], user[ "pub_key" ], user[ "sign_count" ], "icnml.unil.ch"
    )

    webauthn_assertion_response = webauthn.WebAuthnAssertionResponse( 
        webauthn_user,
        assertion_response,
        challenge,
        config.ORIGIN,
        uv_required = False
    )
    
    try:
        webauthn_assertion_response.verify()
        current_app.logger.info( "Webauthn assertion verified" )
        
    except Exception as e:
        return jsonify( {
            "error": True,
            "message": "Assertion failed. Error: {}".format( e )
        } )
    
    ############################################################################
    
    if len( challenge ) % 4 != 0:
        challenge += "=" * ( 4 - ( len( challenge ) % 4 ) )
    
    newuser = base64.b64decode( challenge )
    newuser = json.loads( newuser )
    user_type = int( newuser[ "user" ][ "account_type" ] )
    email = newuser[ "user" ][ "email" ]
    email_hash = utils.hash.pbkdf2( email, utils.rand.random_data( config.EMAIL_SALT_LENGTH ), config.EMAIL_NB_ITERATIONS ).hash()
    request_id = newuser[ "user" ][ "id" ]
    username_id = newuser[ "user" ][ "username_id" ]
    
    n = config.db.query_fetchone( "SELECT name FROM account_type WHERE id = %s", ( user_type, ) )[ "name" ]
    
    username = "{}_{}".format( n, username_id )
    username = username.lower()
    
    current_app.logger.info( "Creation of the new user '{}'".format( username ) )
    
    try:
        config.db.query( "UPDATE signin_requests SET validation_time = now(), assertion_response = %s, status = 'validated' WHERE id = %s", ( assertion_response_s, request_id ) )
        config.db.query( utils.sql.sql_insert_generate( "users", [ "username", "email", "type" ] ), ( username, email_hash, user_type ) )
        
        current_app.logger.debug( "User '{}' created".format( username ) )
    
    except:
        current_app.logger.error( "Error while creating the user account for '{}'".format( username ) )
        
        return jsonify( {
            "error": True,
            "message": "Can not insert into database."
        } )
    
    ############################################################################
    
    try:
        email_content = utils.template.render_jinja_html( 
            "templates/email", "signin.html",
            username = username,
            url = "https://icnml.unil.ch" + url_for( "newuser.config_new_user", uuid = newuser[ "user" ][ "uuid" ] )
        )
        
        msg = MIMEText( email_content, "html" )
        
        msg[ "Subject" ] = "ICNML - Login information"
        msg[ "From" ] = config.sender
        msg[ "To" ] = email
        
        current_app.logger.info( "Sending the email to the user '{}'".format( username ) )
        
        with utils.mail.mySMTP() as s:
            s.sendmail( config.sender, [ email ], msg.as_string() )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True,
            "message": "Error while sending the email"
        } )

@newuser_view.route( "/do/validation_reject", methods = [ "POST" ] )
def do_validation_reject():
    """
        Reject the request for a new user.
    """
    request_id = request.form.get( "id" )
    
    current_app.logger.info( "Reject the new user request {}".format( request_id ) )
    
    try:
        sql = "UPDATE signin_requests SET status = 'rejected' WHERE id = %s"
        config.db.query( sql, ( request_id, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@newuser_view.route( "/config/<uuid>" )
def config_new_user( uuid ):
    """
        Serve the first page to the new user to configure his account.
    """
    current_app.logger.info( "Serve user account configuration page" )
    
    sql = """
        SELECT
            email,
            username_id,
            account_type.name AS account_type
        FROM signin_requests
        LEFT JOIN account_type ON signin_requests.account_type = account_type.id
        WHERE uuid = %s
    """
    r = config.db.query_fetchone( sql, ( uuid, ) )
    
    username = "{}_{}".format( r[ "account_type" ].lower(), r[ "username_id" ] )
    session[ "username" ] = username
    sql = """
        SELECT
            password, totp
        FROM users
        WHERE
            username = %s
    """
    user_match = config.db.query_fetchone( sql, ( username, ) )
    has_password = user_match.get( "password", None ) != None
    has_totp = user_match.get( "totp", None ) != None
    
    try:
        email = r[ "email" ]
        session[ "signin_user_validation_email" ] = email
        session[ "signin_user_validation_uuid" ] = uuid
        
        return utils.template.my_render_template( 
            "login/users/config.html",
            has_password = has_password,
            has_totp = has_totp,
            secret = views.login.get_secret()
        )
    
    except:
        return redirect( url_for( "base.home" ) )

@newuser_view.route( "/do/config", methods = [ "POST" ] )
def do_config_new_user():
    """
        Save the configuration of the new user to the database.
    """
    current_app.logger.info( "Start user account configuration" )
    
    email = session[ "signin_user_validation_email" ]
    uuid = session[ "signin_user_validation_uuid" ]
    username = request.form.get( "username" )
    password = request.form.get( "password" )
    
    session[ "username" ] = username
    
    ############################################################################
    
    r = config.db.query_fetchone( "SELECT count(*) FROM signin_requests WHERE uuid = %s AND email = %s", ( uuid, email, ) )
    r = r[ 0 ]
    
    if r == 0:
        return jsonify( {
            "error": True,
            "message": "no signin request"
        } )
    
    user = config.db.query_fetchone( "SELECT * FROM users WHERE username = %s", ( username, ) )
    
    if user == None:
        current_app.logger.error( "No user found in the databse for '{}'".format( username ) )
        
        return jsonify( {
            "error": True,
            "message": "no user"
        } )
    
    elif not password.startswith( "pbkdf2" ):
        current_app.logger.error( "Password not hashed with PBKDF2" )
        
        return jsonify( {
            "error": True,
            "message": "password not in the correct format"
        } )
    
    elif not utils.hash.pbkdf2( email ).verify( user[ "email" ] ):
        current_app.logger.error( "Email not corresponding to the stored email in the database" )
        
        return jsonify( {
            "error": True,
            "message": "email not corresponding to the request form"
        } )
    
    elif user.get( "password", None ) != None:
        current_app.logger.error( "Password already set for this user" )
        return jsonify( {
            "error": True,
            "message": "password already set"
        } )
    
    ############################################################################
    
    # Check outdated email hash
    _, _, salt, iterations, _ = user[ "email" ].split( "$" )
    iterations = int( iterations )
    
    if iterations != config.EMAIL_NB_ITERATIONS or len( salt ) != config.EMAIL_SALT_LENGTH:
        new_email_hash = utils.hash.pbkdf2(
            email,
            utils.rand.random_data( config.EMAIL_SALT_LENGTH ),
            config.EMAIL_NB_ITERATIONS
        ).hash()
        
        config.db.query( "UPDATE users SET email = %s WHERE id = %s", ( new_email_hash, user[ "id" ] ) )
    
    ############################################################################
    
    current_app.logger.debug( "Storing the new password to the databse" )
    
    password = utils.hash.pbkdf2( password, utils.rand.random_data( config.PASSWORD_SALT_LENGTH ), config.PASSWORD_NB_ITERATIONS ).hash()
    
    config.db.query( "UPDATE users SET password = %s WHERE username = %s", ( password, username, ) )
    
    views.pianos.do_pianos_update_all_accounts()
    
    session[ "username" ] = username
    
    ############################################################################
    
    return jsonify( {
        "error": False
    } )

@newuser_view.route( "/config/donor/<h>" )
def config_new_user_donor( h ):
    """
        Serve the configuration page for a new donor.
    """
    current_app.logger.info( "Start new donor configuration" )
    
    session.clear()
    
    current_app.logger.debug( "Searching in the database for hash value '{}'".format( h ) )
    sql = """
        SELECT users.id, users.username, users.email
        FROM users
        LEFT JOIN account_type ON users.type = account_type.id
        WHERE account_type.name = 'Donor' AND password IS NULL
    """
    for r in config.db.query_fetchall( sql ):
        if h == hashlib.sha512( r[ "email" ] ).hexdigest():
            current_app.logger.info( "User '{}' found".format( r[ "username" ] ) )
            user = r
            break
    
    else:
        current_app.logger.error( "The hash '{}' is not present in the users database".format( h ) )
        return redirect( url_for( "base.home" ) )
    
    session[ "email_hash" ] = h
    session[ "user_id" ] = user[ "id" ]
    
    current_app.logger.info( "Serving the config new donor page" )
    
    return utils.template.my_render_template( 
        "login/users/config.html",
        next_step = "newuser.do_config_new_donor",
        hash = h
    )

@newuser_view.route( "/do/config/donor", methods = [ "POST" ] )
def do_config_new_donor():
    """
        Save the donor configuration to the database.
    """
    current_app.logger.info( "Start donor configuration" )
    
    username = request.form.get( "username" )
    
    current_app.logger.debug( "Username: {}".format( username ) )
    
    password = request.form.get( "password" )
    password = utils.hash.pbkdf2( password, utils.rand.random_data( config.PASSWORD_SALT_LENGTH ), config.PASSWORD_NB_ITERATIONS ).hash()
    h = request.form.get( "hash" )
    
    sql = "SELECT id FROM users WHERE username = %s"
    user_id = config.db.query_fetchone( sql, ( username, ) )[ "id" ]
    
    session[ "username" ] = username
    
    if session[ "email_hash" ] == h and session[ "user_id" ] == user_id:
        config.db.query( "UPDATE users SET password = %s WHERE username = %s", ( password, username, ) )
        
        views.pianos.do_pianos_update_all_accounts()
        
        current_app.logger.info( "Password set" )
        
        return jsonify( {
            "error": False
        } )
    
    else:
        current_app.logger.error( "Error while updating the password dor {}".format( username ) )
        return jsonify( {
            "error": True,
            "message": "Invalid parameters"
        } )
