#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import abort, redirect, jsonify, send_file
from flask import url_for, request, current_app, session

from cStringIO import StringIO
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from threading import Thread
from uuid import uuid4
import base64
import hashlib
import ipaddress
import json
import pyotp
import pytz
import qrcode
import time
import webauthn

import config
import utils
import views

login_view = Blueprint( "login", __name__, template_folder = "templates" )

@login_view.route( "/is_logged" )
def is_logged():
    """
        App route to know if the user is logged in the ICNML main application.
        This route is used by nginx to protect some other locations, for
        example the PiAnoS dedicated pages.
    """
    current_app.logger.info( "Check if the user is connected" )
    
    if session.get( "logged", False ):
        return "ok"
    
    else:
        return abort( 403 )

@login_view.route( "/logout" )
def logout():
    """
        Logout the user, clear the session and redirect to the login page.
    """
    current_app.logger.info( "Logout and clear session" )
    
    session_clear_and_prepare()
    return redirect( url_for( "login.login" ) )

def session_clear_and_prepare():
    """
        Clear the session related to the user and initialize the login related
        variables.
    """
    session.clear()
    
    session[ "process" ] = "login"
    session[ "need_to_check" ] = [ "password" ]
    session[ "logged" ] = False

@login_view.route( "/login" )
def login():
    """
        Route to serve the login.html page.
    """
    current_app.logger.info( "Login start" )
    
    session_clear_and_prepare()
    
    if request.query_string != "":
        session[ "url_redirect" ] = request.query_string
    
    return utils.template.my_render_template( "login/login.html" )

@login_view.route( "/do/login", methods = [ "POST" ] )
def do_login():
    """
        Function to manadge the login workflow and check the username, password
        and TOTP data. This function is called multiple times because the check
        is done only for one data type at the time. If all the checks are OK,
        the user has provided all needed information, hence is logged in.
    """
    #TODO: combine the security key checks in this function
    
    ############################################################################
    #   Rate limiting check
    
    def get_rate_limit_key():
        target = request.form.get( "username", "" )
        
        try:
            target = request.headers.environ[ "REMOTE_ADDR" ]
        except:
            pass
            
        try:
            target = str( ipaddress.ip_network( unicode( target ) ).supernet( 16 ) )
        except:
            pass
        
        return "rate_limit_{}".format( target )
    
    def get_current_rate_limit():
        try:
            return int( config.redis_dbs[ "rate_limit" ].get( get_rate_limit_key() ) )
        except:
            return 1
    
    def rate_limit_to_seconds( nb ):
        return pow( config.login_rate_limiting_base, max( nb, config.login_rate_limiting_limit ) )
    
    def trigger_rate_limit():
        rate_limit_value = get_current_rate_limit() + 1
        
        config.redis_dbs[ "rate_limit" ].set(
            get_rate_limit_key(),
            rate_limit_value,
            ex = rate_limit_to_seconds( rate_limit_value )
        )
        
        return rate_limit_value
    
    if get_current_rate_limit() >= config.login_rate_limiting_limit:
        rate_limit_value = trigger_rate_limit()
        time_to_wait = str( timedelta( seconds = rate_limit_to_seconds( rate_limit_value ) ) )
        
        return jsonify( {
            "error": False,
            "logged": False,
            "message": "Rate limited. Wait {} (HH:MM:SS) or contact the administrator.".format( time_to_wait )
        } )
    
    ############################################################################
    #   Start of the user and password check
    
    need_to_check = session.get( "need_to_check", [ "password" ] )
    try:
        current_check = need_to_check[ 0 ]
    except:
        current_check = None
    
    session[ "need_to_check" ] = need_to_check
    
    current_app.logger.info( "Current check: {}".format( current_check ) )
    
    ############################################################################
    #   Username and password check

    if current_check == "password":
        user = config.db.query_fetchone( "SELECT * FROM users WHERE username = %s", ( request.form.get( "username" ), ) )
        
        if user == None:
            current_app.logger.error( "Username not found in the database" )
            
            # WASTING TIME.
            # This is done to limit data extraction for exitsing (or not)
            # username based upon the execution time of the login function
            # (time-based side channel attack).
            # FOR SECURITY REASONS, DO NOT REMOVE THIS LINE
            utils.hash.pbkdf2( config.fake_hash ).verify( config.fake_hash_stored )
            
            trigger_rate_limit()
            
            session_clear_and_prepare()
            
            return jsonify( {
                "error": False,
                "logged": False
            } )
        
        form_password = request.form.get( "password", None )
        
        if form_password == None or not utils.hash.pbkdf2( form_password ).verify( user[ "password" ] ):
            current_app.logger.error( "Password not validated" )
            
            trigger_rate_limit()
            
            session_clear_and_prepare()
            
            return jsonify( {
                "error": False,
                "logged": False,
            } )
        
        elif not user[ "active" ]:
            current_app.logger.error( "User not active" )
            
            session_clear_and_prepare()
            
            return jsonify( {
                "error": False,
                "logged": False,
                "message": "Your account is not activated. Please contact an administrator (icnml@unil.ch)."
            } )
        
        else:
            session[ "username" ] = user[ "username" ]
            session[ "user_id" ] = user[ "id" ]
            session[ "password_check" ] = True
            
            # Check for outdated password and update it in the database if needed
            _, _, salt, iterations, _ = user[ "password" ].split( "$" )
            iterations = int( iterations )
            
            if iterations != config.PASSWORD_NB_ITERATIONS or len( salt ) != config.PASSWORD_SALT_LENGTH:
                new_password = utils.hash.pbkdf2(
                    form_password,
                    utils.rand.random_data( config.PASSWORD_SALT_LENGTH ),
                    config.PASSWORD_NB_ITERATIONS
                ).hash()
                config.db.query( "UPDATE users SET password = %s WHERE id = %s", ( new_password, user[ "id" ] ) )
            
            #
            current_app.logger.info( "User '{}' checked by password".format( user[ "username" ] ) )
            
            session[ "need_to_check" ].remove( current_check )
            session[ "password" ] = utils.hash.pbkdf2( form_password, "AES256", config.PASSWORD_NB_ITERATIONS ).hash()
            
            sql = "SELECT count( * ) FROM webauthn WHERE user_id = %s AND active = TRUE"
            security_keys_count = config.db.query_fetchone( sql, ( user[ "id" ], ) )[ "count" ]
            
            current_app.logger.info( "Number of security keys: {}".format( security_keys_count ) )
            current_app.logger.info( "TOTP: {}".format( user[ "totp" ] is not None ) )
            
            if config.envtype.upper() != "DEV":
                hra = hashlib.sha512( request.headers.environ[ "REMOTE_ADDR" ] ).hexdigest()
                username = session[ "username" ]
                key = "{}_{}".format( username, hra )
                saved_totp = config.redis_dbs[ "totp" ].get( key ) == "ok"
                
                if security_keys_count > 0:
                    session[ "need_to_check" ].append( "securitykey" )
                
                else:
                    if saved_totp:
                        config.redis_dbs[ "totp" ].set( key, "ok", ex = 30 * 24 * 3600 )
                        pass
                    
                    elif user[ "totp" ]:
                        session[ "need_to_check" ].append( "totp" )
                    
                    else:
                        current_app.logger.error( "Second factor missing" )
                        
                        session_clear_and_prepare()
                        
                        return jsonify( {
                            "error": False,
                            "logged": False,
                            "next_step": "totp_reset"
                        } )
    
    ############################################################################
    #   Time-based One Time Password check

    elif current_check == "totp":
        user = config.db.query_fetchone( "SELECT username, totp FROM users WHERE username = %s", ( session[ "username" ], ) )
        
        totp_db = pyotp.TOTP( user[ "totp" ] )
        totp_user = request.form.get( "totp", None )
        totp_save_serverside = request.form.get( "save", False )
        
        if totp_user == None:
            return jsonify( {
                "error": True,
                "message": "No TOTP provided"
            } )
        
        current_app.logger.info( "TOTP expected now: {}".format( totp_db.now() ) )
        current_app.logger.info( "TOTP provided:     {}".format( totp_user ) )
        
        if not totp_db.verify( totp_user, valid_window = config.TOTP_VALIDWINDOW ):
            current_app.logger.error( "TOTP not valid in a {} time window".format( config.TOTP_VALIDWINDOW ) )
            current_app.logger.info( "TOTP check for a bigger time window" )
            
            # Check for a possible time difference
            now = datetime.now()
            time_diff = None
            try:
                for i in xrange( config.TOTP_VALIDWINDOW, config.TOTP_MAX_VALIDWINDOW ):
                    for m in [ -1, 1 ]:
                        if pyotp.utils.strings_equal( totp_user, totp_db.at( now, i * m ) ):
                            raise Exception( "TOTP valid out of current time window" )
                
                else:
                    current_app.logger.error( "TOTP not valid for this secret in a timeframe of {}".format( config.TOTP_MAX_VALIDWINDOW ) )
            
            except:
                time_diff = i * m * totp_db.interval
                current_app.logger.info( "TOTP valid for {} seconds".format( time_diff ) )
            
            # Error return
            session[ "logged" ] = False
            return jsonify( {
                "error": False,
                "logged": False,
                "message": "Wrong TOTP",
                "time_diff": time_diff,
                "time": time.time()
            } )
        
        else:
            current_app.logger.info( "Valid TOTP in a {} time window".format( config.TOTP_VALIDWINDOW ) )
            
            if totp_save_serverside in [ True, "true" ]:
                hra = hashlib.sha512( request.headers.environ[ "REMOTE_ADDR" ] ).hexdigest()
                username = session[ "username" ]
                key = "{}_{}".format( username, hra )
                
                config.redis_dbs[ "totp" ].set( key, "ok", ex = 30 * 24 * 3600 )
                
            session[ "need_to_check" ].remove( current_check )
    
    ############################################################################
    #   Check if all the data has been provided; login if ok

    if len( session[ "need_to_check" ] ) == 0 and session.get( "password_check", False ):
        for key in [ "process", "need_to_check", "password_check" ]:
            if key in session:
                session.pop( key )
        
        session[ "logged" ] = True
        current_app.logger.info( "User '{}' connected".format( session[ "username" ] ) )
        
        sql = """
            SELECT users.type, account_type.name as account_type_name
            FROM users
            LEFT JOIN account_type ON users.type = account_type.id
            WHERE username = %s
        """
        user = config.db.query_fetchone( sql, ( session[ "username" ], ) )
        session[ "account_type" ] = int( user[ "type" ] )
        session[ "account_type_name" ] = user[ "account_type_name" ]
        
        config.redis_dbs[ "sessions" ].execute_command( "save" )
        
        return jsonify( {
            "error": False,
            "logged": True,
        } )
    
    else:
        current_app.logger.info( "Push '{}' as next login step".format( session[ "need_to_check" ][ 0 ] ) )
        
        return jsonify( {
            "error": False,
            "next_step": session[ "need_to_check" ][ 0 ]
        } )

################################################################################
#    webauthn keys

@login_view.route( "/webauthn/admin" )
@utils.decorator.login_required
def webauthn_admin():
    """
        Serve the administartion page for the FIDO2 keys.
    """
    current_app.logger.info( "Webauthn admin page" )
    
    return utils.template.my_render_template( 
        "login/webauthn/admin.html",
        keys = do_webauthn_get_list_of_keys( all_keys = True )
    )

def do_webauthn_get_list_of_keys( uid = None, all_keys = False ):
    """
        Get the list of keys for a particular user. Can be filtered by active
        keys only with the `all_keys` parameter. If the user id (uid) variable
        is not passed in parameter, the id of the currently logged user will be
        used (via the session).
    """
    user_id = session.get( "user_id", uid )
    
    current_app.logger.info( "Retrieving the security keys for user '{}'".format( session[ "username" ] ) )
    
    sql = """
        SELECT
            id, key_name as name,
            created_on, last_usage, usage_counter,
            active
        FROM webauthn
        WHERE user_id = %s
    """
    if not all_keys:
        sql += " AND active = true"
    sql += " ORDER BY key_name ASC"
    
    data = config.db.query_fetchall( sql, ( user_id, ) )
    
    return data

@login_view.route( "/webauthn/begin_activate", methods = [ "POST" ] )
@utils.decorator.login_required
def webauthn_begin_activate():
    """
        Start the registering process for a new security key. The json returned
        will be used by the javascript navigator.credentials.create() function.
    """
    current_app.logger.info( "Start the registring process for a new security key" )
    
    session[ "key_name" ] = request.form.get( "key_name", None )
    
    username = session.get( "username" )
    
    challenge = pyotp.random_base32( 64 )
    ukey = pyotp.random_base32( 64 )
    
    current_app.logger.debug( "User: {}".format( username ) )
    current_app.logger.debug( "Challenge: {}".format( challenge ) )
    
    session[ "challenge" ] = challenge
    session[ "register_ukey" ] = ukey
    
    make_credential_options = webauthn.WebAuthnMakeCredentialOptions( 
        challenge, config.rp_name, config.RP_ID,
        ukey, username, username,
        None
    )
    
    registration_dict = make_credential_options.registration_dict
    registration_dict[ "authenticatorSelection" ] = {
        "authenticatorAttachment": "cross-platform",
        "requireResidentKey": False,
        "userVerification": "discouraged"
    }
    
    return jsonify( registration_dict )

@login_view.route( "/webauthn/verify", methods = [ "POST" ] )
@utils.decorator.login_required
def webauthn_verify():
    """
        Verify the data produced by the security key while registring
        (with the navigator.credentials.create() function).
    """
    current_app.logger.info( "Start webauthn verification process" )
    
    challenge = session[ "challenge" ]
    user_id = session[ "user_id" ]
    key_name = session.get( "key_name", None )
    ukey = session[ "register_ukey" ]
    
    current_app.logger.debug( "Session challenge: {}".format( challenge ) )
    current_app.logger.debug( "Session user_id: {}".format( user_id ) )
    current_app.logger.debug( "Session key_name: {}".format( key_name ) )
    
    webauthn_registration_response = webauthn.WebAuthnRegistrationResponse( 
        config.RP_ID,
        config.ORIGIN,
        request.form,
        challenge
    )
    
    try:
        webauthn_credential = webauthn_registration_response.verify()
        current_app.logger.info( "Verification OK" )
    
    except Exception as e:
        current_app.logger.info( "Verification failed" )
        
        return jsonify( {
            "error": True,
            "message": "Registration failed. Error: {}".format( e )
        } )
    
    try:
        current_app.logger.info( "Insertion of the key to the database" )
        
        config.db.query( 
            utils.sql.sql_insert_generate( "webauthn", [ "user_id", "key_name", "ukey", "credential_id", "pub_key", "sign_count" ] ),
            ( 
                user_id, key_name,
                ukey, webauthn_credential.credential_id,
                webauthn_credential.public_key, webauthn_credential.sign_count,
            )
        )
        
        return jsonify( {
            "success": "User successfully registered."
        } )
    
    except:
        current_app.logger.error( "Database insertion error" )
        
        return jsonify( {
            "error": True,
            "message": "Database error"
        } )

################################################################################

@login_view.route( "/webauthn/delete", methods = [ "POST" ] )
@utils.decorator.login_required
def webauthn_delete_key():
    """
        Delete a key based upon the key id and name for the currently logged user.
    """
    current_app.logger.info( "Start security deletion" )
    
    key_id = request.form.get( "key_id", False )
    userid = session[ "user_id" ]
    
    current_app.logger.debug( "Session username: {}".format( session[ "username" ] ) )
    current_app.logger.debug( "key_id: {}".format( key_id ) )
    
    try:
        config.db.query( "DELETE FROM webauthn WHERE id = %s AND user_id = %s", ( key_id, userid, ) )
        
        current_app.logger.debug( "Security key deleted" )
        
        return jsonify( {
            "error": False
        } )
        
    except:
        current_app.logger.error( "Security key deletion failed" )
        
        return jsonify( {
            "error": True
        } )

@login_view.route( "/webauthn/disable", methods = [ "POST" ] )
@utils.decorator.login_required
def webauthn_disable_key():
    """
        Disable a particular security key for the current user.
    """
    key_id = request.form.get( "key_id", False )
    userid = session[ "user_id" ]
    
    current_app.logger.info( "Disabling key '{}' for user '{}'".format( key_id, session[ "username" ] ) )
    
    try:
        config.db.query( "UPDATE webauthn SET active = False WHERE id = %s AND user_id = %s", ( key_id, userid, ) )
        
        current_app.logger.debug( "Key disabled" )
        
        return jsonify( {
            "error": False
        } )
        
    except:
        current_app.logger.error( "Key disabling database error" )
        
        return jsonify( {
            "error": True
        } )

@login_view.route( "/webauthn/enable", methods = [ "POST" ] )
@utils.decorator.login_required
def webauthn_enable_key():
    """
        Activation of a security key for the current user.
    """
    key_id = request.form.get( "key_id", False )
    userid = session[ "user_id" ]
    
    current_app.logger.info( "Enabling key '{}' for user '{}'".format( key_id, session[ "username" ] ) )
    
    try:
        config.db.query( "UPDATE webauthn SET active = True WHERE id = %s AND user_id = %s", ( key_id, userid, ) )
        
        current_app.logger.debug( "Key enabled" )
        
        return jsonify( {
            "error": False
        } )
        
    except:
        current_app.logger.error( "Key enabling database error" )
        
        return jsonify( {
            "error": True
        } )

@login_view.route( "/webauthn/rename", methods = [ "POST" ] )
@utils.decorator.login_required
def webauthn_rename_key():
    """
        Rename a security key for the current user.
    """
    key_id = request.form.get( "key_id", False )
    key_name = request.form.get( "key_name", False )
    userid = session[ "user_id" ]
    
    current_app.logger.info( "Renaming key '{}' for user '{}'".format( key_id, session[ "username" ] ) )
    
    try:
        config.db.query( "UPDATE webauthn SET key_name = %s WHERE id = %s AND user_id = %s", ( key_name, key_id, userid, ) )
        
        current_app.logger.debug( "Key renamed" )
        
        return jsonify( {
            "error": False
        } )
        
    except:
        current_app.logger.error( "Key renaming error" )
        return jsonify( {
            "error": True
        } )

@login_view.route( "/webauthn/begin_assertion" )
def webauthn_begin_assertion():
    """
        Get the data to start the login process with all actives keys for a user.
    """
    current_app.logger.info( "Webauthn start data preparation for user '{}'".format( session[ "username" ] ) )
    
    user_id = session.get( "user_id" )
    
    if "challenge" in session:
        del session[ "challenge" ]
    
    challenge = pyotp.random_base32( 64 )
    session[ "challenge" ] = challenge
    
    current_app.logger.debug( "Challenge: '{}'".format( challenge ) )
    
    key_list = config.db.query_fetchall( "SELECT * FROM webauthn WHERE user_id = %s AND active = true", ( user_id, ) )
    
    current_app.logger.info( "{} keys active for this user".format( len( key_list ) ) )
    
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

@login_view.route( "/webauthn/verify_assertion", methods = [ "POST" ] )
def webauthn_verify_assertion():
    """
        Check the signed challenge provided to the user for the login process.
    """
    current_app.logger.info( "Webauthn start assertion verification" )
    
    challenge = session.get( "challenge" )
    assertion_response = request.form
    credential_id = assertion_response.get( "id" )
    
    current_app.logger.debug( "Used key: '{}'".format( credential_id ) )
    
    user = config.db.query_fetchone( "SELECT * FROM webauthn WHERE credential_id = %s", ( credential_id, ) )
    
    for key in [ "sign_count", "created_on", "last_usage", "usage_counter" ]:
        current_app.logger.debug( "key {}: {}".format( key, user[key] ) )
    
    webauthn_user = webauthn.WebAuthnUser( 
        None, session[ "username" ], None, None,
        user[ "credential_id" ], user[ "pub_key" ], user[ "sign_count" ], config.RP_ID
    )

    webauthn_assertion_response = webauthn.WebAuthnAssertionResponse( 
        webauthn_user,
        assertion_response,
        challenge,
        config.ORIGIN,
        uv_required = False
    )
    
    try:
        sign_count = webauthn_assertion_response.verify()
        current_app.logger.info( "Webauthn key verified" )
        
    except Exception as e:
        current_app.logger.error( "Webauthn assertion failed" )
        
        return jsonify( {
            "error": True,
            "message": "Assertion failed. Error: {}".format( e )
        } )
    
    else:
        current_app.logger.debug( "Update key usage in the database" )
        
        dt = datetime.now( pytz.timezone( "Europe/Zurich" ) )
        config.db.query( "UPDATE webauthn SET sign_count = %s, last_usage = %s, usage_counter = usage_counter + 1 WHERE credential_id = %s", ( sign_count, dt, credential_id, ) )
        
        session[ "need_to_check" ].remove( "securitykey" )
        do_login()
        
        return jsonify( {
            "error": False
        } )

@login_view.route( "/reset_password" )
def password_reset():
    """
        Serve the password_reset.html page.
    """
    session.clear()
    session[ "process" ] = "request_password_reset"
    
    return utils.template.my_render_template( "login/users/password_reset.html" )

@login_view.route( "/do/reset_password", methods = [ "POST" ] )
def do_password_reset():
    """
        Start the check of the username for a password reset. The check is done
        in a thread to allow a fast "OK" response, even if the username does
        not exists. This prevent data extraction (presence or not of a
        username).
    """
    email = request.form.get( "email", None )
    
    current_app.logger.info( "Start a password reset procedure for '{}'".format( email ) )
    
    Thread( target = do_password_reset_thread, args = ( email, current_app._get_current_object(), ) ).start()
    
    return jsonify( {
        "error": False,
        "message": "OK"
    } )

def do_password_reset_thread( email, localapp ):
    """
        Search in the database if the provided email is present, and send the
        password reset email if so.
    """
    if email == None:
        return False

    else:
        users = config.db.query_fetchall( "SELECT id, username, email FROM users ORDER BY username ASC" )
        
        found = []
        
        for user in users:
            localapp.logger.debug( "Password reset - Checking '{}' against '{}'".format( email, user[ "username" ] ) )
            
            if not user[ "email" ].startswith( "pbkdf2$" ):
                continue
            
            elif utils.hash.pbkdf2( email ).verify( user[ "email" ] ):
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
                
                ####################################################################
                
                user_id = hashlib.sha512( utils.rand.random_data( 100 ) ).hexdigest()
                
                ####################################################################
                
                data = {
                    "process": "password_reset",
                    "process_id": user_id,
                    "user_id": user[ "id" ]
                }
                data = json.dumps( data )
                data = base64.b64encode( data )
                
                reset_id = "reset_{}".format( user_id )
                config.redis_dbs[ "reset" ].set( reset_id, data, ex = 24 * 3600 )
                
                ####################################################################
                
                with localapp.app_context(), localapp.test_request_context():
                    url = config.domain + url_for( "login.password_reset_stage2", user_id = user_id )
                
                email_content = utils.template.render_jinja_html( 
                    "templates/email", "reset.html",
                    url = url,
                    username = user[ "username" ]
                )
                
                msg = MIMEText( email_content, "html" )
                
                msg[ "Subject" ] = "ICNML - User password reset"
                msg[ "From" ] = config.sender
                msg[ "To" ] = email
                
                with utils.mail.mySMTP() as s:
                    s.sendmail( config.sender, [ email ], msg.as_string() )
                
                found.append( user[ "username" ] )
                
        if len( found ) > 0:
            localapp.logger.info( "Password reset - '{}' found against {}".format( email, ", ".join( found ) ) )
        else:
            localapp.logger.error( "Password reset - '{}' not found".format( email ) )

@login_view.route( "/reset_password_stage2/<user_id>", methods = [ "GET", "POST" ] )
def password_reset_stage2( user_id ):
    """
        Serve the reset password, second stage (password edit fields) page,
        and set the data in the database if provided.
    """
    current_app.logger.info( "Starting password reset stage 2" )
    
    reset_id = "reset_{}".format( user_id )
    data = config.redis_dbs[ "reset" ].get( reset_id )
    
    if data != None:
        data = base64.b64decode( data )
        data = json.loads( data )
        
        password = request.form.get( "password", None )
        
        userid = data.get( "user_id", None )
        
        if password != None:
            password = utils.hash.pbkdf2( password, utils.rand.random_data( config.PASSWORD_SALT_LENGTH ), config.PASSWORD_NB_ITERATIONS ).hash()
            config.db.query( "UPDATE users SET password = %s WHERE id = %s", ( password, userid ) )
            
            views.pianos.do_pianos_update_all_accounts()
            
            current_app.logger.debug( "Password updated for user id '{}'".format( userid ) )
            
            reset_id = "reset_{}".format( user_id )
            config.redis_dbs[ "reset" ].delete( reset_id )
            
            return jsonify( {
                "error": False,
                "password_updated": True
            } )
            
        else:
            current_app.logger.debug( "Password reset template render" )
            
            return utils.template.my_render_template( 
                "login/users/password_reset_stage2.html",
                user_id = user_id
            ) 
        
    else:
        current_app.logger.error( "No reset procedure found for '{}'".format( user_id ) )
        
        return jsonify( {
            "error": True,
            "message": "Reset procedure not found/expired"
        } )

################################################################################
#    TOTP reset

@login_view.route( "/reset_totp" )
def totp_reset():
    """
        Serve the password_reset.html page.
    """
    session.clear()
    session[ "process" ] = "request_totp_reset"
    
    return utils.template.my_render_template( "login/users/totp_reset.html" )

@login_view.route( "/do/reset_totp", methods = [ "POST" ] )
def do_totp_reset():
    """
        Start the check of the username for a TOTP reset.
        The check is done in a thread to allow a fast "OK" response, even if the username
        does not exists. This prevent data extraction (presence or not of a username).
    """
    email = request.form.get( "email", None )
    
    current_app.logger.info( "Start a TOTP reset procedure for '{}'".format( email ) )
    
    Thread( target = do_totp_reset_thread, args = ( email, current_app._get_current_object(), ) ).start()
    
    return jsonify( {
        "error": False,
        "message": "OK"
    } )

def do_totp_reset_thread( email, localapp ):
    """
        Search in the database if the provided email is present, and send the
        totp reset email if so.
    """
    if email == None:
        return False

    else:
        users = config.db.query_fetchall( "SELECT id, username, email FROM users" )
        
        found = []
        
        for user in users:
            localapp.logger.debug( "TOTP reset - Checking '{}' against '{}'".format( email, user[ "username" ] ) )
            
            if not user[ "email" ].startswith( "pbkdf2$" ):
                continue
            
            elif utils.hash.pbkdf2( email ).verify( user[ "email" ] ):
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
                    
                ####################################################################
                
                user_id = hashlib.sha512( utils.rand.random_data( 100 ) ).hexdigest()
                
                ####################################################################
                
                data = {
                    "process": "totp_reset",
                    "process_id": user_id,
                    "user_id": user[ "id" ],
                    "username": user[ "username" ]
                }
                data = json.dumps( data )
                data = base64.b64encode( data )
                
                reset_id = "reset_{}".format( user_id )
                config.redis_dbs[ "reset" ].set( reset_id, data, ex = 24 * 3600 )
                
                ####################################################################
                
                with localapp.app_context(), localapp.test_request_context():
                    url = config.domain + url_for( "login.totp_reset_stage2", user_id = user_id )
                
                email_content = utils.template.render_jinja_html( 
                    "templates/email", "reset.html",
                    url = url,
                    username = user[ "username" ]
                )
                
                msg = MIMEText( email_content, "html" )
                
                msg[ "Subject" ] = "ICNML - User TOTP reset"
                msg[ "From" ] = config.sender
                msg[ "To" ] = email
                
                with utils.mail.mySMTP() as s:
                    s.sendmail( config.sender, [ email ], msg.as_string() )
                
                found.append( user[ "username" ] )
                
        if len( found ) > 0:
            localapp.logger.info( "TOTP reset - '{}' found against {}".format( email, ", ".join( found ) ) )
        else:
            localapp.logger.error( "TOTP reset - '{}' not found".format( email ) )

@login_view.route( "/reset_totp_stage2/<user_id>", methods = [ "GET", "POST" ] )
def totp_reset_stage2( user_id ):
    """
        Serve the reset totp, second stage (password edit fields) page, and set
        the data in the database if provided.
    """
    current_app.logger.info( "Starting TOTP reset stage 2" )
    
    reset_id = "reset_{}".format( user_id )
    data = config.redis_dbs[ "reset" ].get( reset_id )
    
    if data != None:
        data = base64.b64decode( data )
        data = json.loads( data )
        
        totp = request.form.get( "totp", None )
        
        userid = data.get( "user_id", None )
        session[ "username" ] = data.get( "username", None )
        
        if totp != None:
            config.db.query( "UPDATE users SET totp = %s WHERE id = %s", ( totp, userid ) )
            
            current_app.logger.debug( "totp updated for user id '{}'".format( userid ) )
            
            reset_id = "reset_{}".format( user_id )
            config.redis_dbs[ "reset" ].delete( reset_id )
            
            return jsonify( {
                "error": False,
                "totp_updated": True
            } )
            
        else:
            current_app.logger.debug( "TOTP reset template render" )
            
            return utils.template.my_render_template( 
                "login/users/totp_reset_stage2.html",
                user_id = user_id,
                secret = get_secret()
            ) 
        
    else:
        current_app.logger.error( "No reset procedure found for '{}'".format( user_id ) )
        
        return jsonify( {
            "error": True,
            "message": "Reset procedure not found/expired"
        } )

@login_view.route( "/totp_help" )
def totp_help():
    """
        Serve the help page for the TOTP.
    """
    current_app.logger.info( "Serving the TOTP help page" )
    return utils.template.my_render_template( "login/totp_help.html" )

################################################################################
#    QR Code generation

def renew_secret():
    """
        Request a new TOTP secret.
    """
    current_app.logger.info( "Generate new secret" )
    
    secret = pyotp.random_base32( 40 )
    session[ "secret" ] = secret
    
    return secret

def get_secret():
    """
        Retrieve the current secret.
    """
    current_app.logger.info( "Request secret for user '{}'".format( session[ "username" ] ) )
    
    secret = session.get( "secret", None )
    if secret == None:
        secret = renew_secret()
    
    return secret

@login_view.route( "/set_secret" )
def set_secret():
    """
        Set the new secret value for the TOTP in the database.
    """
    current_app.logger.info( "Storing new secret for user '{}'".format( session[ "username" ] ) )
    
    try:
        config.db.query( "UPDATE users SET totp = %s WHERE username = %s", ( session[ "secret" ], session[ "username" ], ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@login_view.route( "/secret" )
def request_secret():
    """
        Serve the current secret as JSON.
    """
    current_app.logger.info( "Request the secret for user '{}'".format( session[ "username" ] ) )
    
    get_secret()
    
    return jsonify( {
        "error": False,
        "secret": session[ "secret" ]
    } )

@login_view.route( "/new_secret" )
def request_renew_secret():
    """
        Serve current secret.
    """
    current_app.logger.info( "Renew TOTP secret for user '{}'".format( session[ "username" ] ) )
    
    renew_secret()
    
    return jsonify( {
        "error": False,
        "secret": session[ "secret" ]
    } )

@login_view.route( "/user/config/totp_qrcode.png" )
def user_totp_qrcode():
    """
        Generate the TOTP PNG QRcode image ready to scan.
    """
    current_app.logger.info( "Generate the TOTP QRcode" )
    
    if "username" in session:
        qrcode_value = "otpauth://totp/ICNML%20{}?secret={}&issuer=ICNML".format( session[ "username" ], get_secret() )
    else:
        qrcode_value = "otpauth://totp/ICNML?secret={}&issuer=ICNML".format( get_secret() )
    
    current_app.logger.debug( "Value: {}".format( qrcode_value ) )
    
    img = qrcode.make( qrcode_value )
    
    temp = StringIO()
    img.save( temp, format = "png" )
    temp.seek( 0 )
    
    return send_file( temp, mimetype = "image/png" )
    
@login_view.route( "/user/config/example_totp_qrcode.png" )
def user_totp_qrcode_example():
    qrcode_value = "otpauth://totp/ICNML%20{}?secret={}&issuer=ICNML".format( "user_name", "secretsecretsecretsecret" )
    
    img = qrcode.make( qrcode_value )
    
    temp = StringIO()
    img.save( temp, format = "png" )
    temp.seek( 0 )
    
    return send_file( temp, mimetype = "image/png" )
@login_view.route( "/user/config/totp" )
@utils.decorator.login_required
def user_totp_config():
    """
        Serve the TOTP configuration page.
    """
    current_app.logger.info( "Serve the TOTP config page" )
    
    return utils.template.my_render_template( 
        "login/users/totp.html",
        secret = get_secret(),
        random_value = time.time()
    )
