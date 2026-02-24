#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import functools

from flask import session
from flask import redirect, abort, url_for
from flask import request

import config
from . import redis

def session_field_required( field, value ):
    """
        Require a field in the `flask.session` to be present and have a certain value.
        The target value is passed in parameter.

        :param field: Field to check for presence
        :type field: str

        :param value: Value to check against
        :type value: any
    """
    def decorator( func ):
        @functools.wraps( func )
        def wrapper_login_required( *args, **kwargs ):
            if not field in session:
                return redirect( url_for( "login.login" ) + "?" + request.path )
            
            elif not session.get( field ) == value:
                return redirect( url_for( "login.login" ) + "?" + request.path )
            
            return func( *args, **kwargs )
    
        return wrapper_login_required
    
    return decorator

def login_required( func ):
    """
        Check for a valid login for the current session.
        This will check if the current session is correctly logged-in (including the second factor).
    """
    @functools.wraps( func )
    def wrapper_login_required( *args, **kwargs ):
        if not session.get( "logged", False ) :
            return redirect( url_for( "login.login" ) + "?" + request.path )
        
        return func( *args, **kwargs )

    return wrapper_login_required

def referer_required( func ):
    """
        Check the presence of the HTTP `referer` field.
    """
    @functools.wraps( func )
    def wrapper_login_required( *args, **kwargs ):
        if not request.headers.get( "Referer", False ):
            return "referrer needed", 404
        
        return func( *args, **kwargs )

    return wrapper_login_required

def admin_required( func ):
    """
        Check if the user is connected and is an administrator.
    """
    @functools.wraps( func )
    def wrapper_login_required( *args, **kwargs ):
        if not session.get( "logged", False ) or not session.get( "account_type_name", None ) == "Administrator":
            return redirect( url_for( "login.login" ) + "?" + request.path )
        
        return func( *args, **kwargs )

    return wrapper_login_required

@redis.redis_cache( 15 * 60 )
def check_correct_submitter( submission_id, submitter_id ):
    """
        Check if the current user is the uploader of the current submission.
    """
    sql = """
        SELECT count( * )
        FROM submissions
        WHERE uuid = %s AND submitter_id = %s
    """
    check = config.db.query_fetchone( sql, ( submission_id, submitter_id, ) )[ "count" ]
    return check == 1

def submission_has_access( func ):
    """
        Will check if the user has access to the current submission.
        This can be the case if the user is an administrator or if he is the submitter of the current submission.
    """
    @functools.wraps( func )
    def wrapper_login_required( *args, **kwargs ):
        submission_id = request.view_args.get( "submission_id", None )
        user_id = session.get( "user_id" )
        
        if session.get( "account_type_name", None ) == "Administrator":
            return func( *args, **kwargs )
        
        elif not session.get( "logged", False ) or not session.get( "account_type_name", None ) == "Submitter":
            return redirect( url_for( "login.login" ) + "?" + request.path )
        
        elif submission_id != None and not check_correct_submitter( submission_id, user_id ):
            return abort( 403 )
        
        else:
            return func( *args, **kwargs )

    return wrapper_login_required

def trainer_has_access( func ):
    """
        Check if the user is a trainer or an administrator.
    """
    @functools.wraps( func )
    def wrapper_trainer_has_access( *args, **kwargs ):
        if session.get( "account_type_name", None ) == "Administrator":
            return func( *args, **kwargs )
        
        elif not session.get( "logged", False ) or not session.get( "account_type_name", None ) == "Trainer":
            return redirect( url_for( "login.login" ) + "?" + request.path )
        
        else:
            return func( *args, **kwargs )

    return wrapper_trainer_has_access

