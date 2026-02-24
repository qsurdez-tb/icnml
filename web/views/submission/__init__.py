#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import current_app, request, jsonify, session, url_for, redirect, abort, send_file

import base64
import hashlib
import json
import zipfile
from uuid import uuid4

from cStringIO import StringIO
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pdf2image
from PIL import Image
from pyzbar import pyzbar

import config
from const import pfsp

import utils
import views

from NIST.fingerprint.labels import SEGMENTS_POSITION_CODE as segments_position_code

submission_view = Blueprint( "submission", __name__, template_folder = "templates" )

@submission_view.route( "/upload", methods = [ "POST" ] )
@utils.decorator.login_required
def upload_file():
    """
        Main function dealing with the upload of files (tenprint, mark and
        consent forms). This function accept traditionals images and NIST files
        for the fingerprint data, and PDFs for the consent forms.
    """
    current_app.logger.info( "Processing of the uploaded file" )
    
    upload_type = request.form.get( "upload_type", None )
    current_app.logger.debug( "Upload type: {}".format( upload_type ) )
    
    file_extension = request.form.get( "extension", None )
    if isinstance( file_extension, str ):
        file_extension = file_extension.lower()
    
    current_app.logger.debug( "File extension: {}".format( file_extension ) )
    
    if upload_type == None:
        return jsonify( {
            "error": True,
            "message": "Must specify a file type to upload a file"
        } )
    
    if "file" not in request.files:
        current_app.logger.error( "No file in the upload request" )
        return jsonify( {
            "error": True,
            "message": "No file in the POST request"
        } )
    
    elif "submission_id" not in request.form:
        current_app.logger.error( "No submission identification number" )
        return jsonify( {
            "error": True,
            "message": "No submission_id"
        } )
    
    else:
        try:
            submission_uuid = request.form.get( "submission_id" )
            sql = "SELECT id FROM submissions WHERE uuid = %s"
            submission_id = config.db.query_fetchone( sql, ( submission_uuid, ) )[ "id" ]
            
            current_app.logger.debug( "Submission UUID: {}".format( submission_uuid ) )
            
        except:
            return jsonify( {
                "error": True,
                "message": "upload not related to a submission form"
            } )
        
        uploaded_file = request.files[ "file" ]
        file_name = utils.encryption.do_encrypt_user_session( uploaded_file.filename )
        file_uuid = str( uuid4() )
        
        current_app.logger.debug( "File uuid: {}".format( file_uuid ) )
        
        fp = StringIO()
        
        uploaded_file.save( fp )
        file_size = fp.tell()
        
        current_app.logger.debug( "File size: {}".format( file_size ) )
        
        fp.seek( 0 )
        
        if file_extension in config.NIST_file_extensions:
            file_data = fp.getvalue()
            file_data = base64.b64encode( file_data )
            file_data = utils.encryption.do_encrypt_dek( file_data, submission_uuid )
            
            # Save the NIST file in the DB
            current_app.logger.info( "Saving the NIST file to the database" )
            sql = utils.sql.sql_insert_generate(
                "files",
                [ "folder", "creator", "filename", "type", "format", "size", "uuid", "data" ]
            )
            data = ( submission_id, session[ "user_id" ], file_name, 5, "NIST", file_size, file_uuid, file_data, )
            config.db.query( sql, data )
            
            return jsonify( {
                "error": False
            } )
                
        else:
            if upload_type in [ "mark_target", "mark_incidental", "tenprint_card_front", "tenprint_card_back" ]:
                current_app.logger.info( "Image file type: {}".format( upload_type ) )
                
                img = Image.open( fp )
                img_format = img.format
                width, height = img.size
                
                current_app.logger.debug( str( img ) )
                
                try:
                    res = int( img.info[ "dpi" ][ 0 ] )
                    current_app.logger.debug( "Resolution: {}".format( res ) )
                except:
                    current_app.logger.error( "No resolution found in the image" )
                    return jsonify( {
                        "error": True,
                        "message": "No resolution found in the image. Upload not possible at the moment."
                    } )
                
                try:
                    img = utils.images.rotate_image_upon_exif( img )
                    current_app.logger.debug( "Rotation of the image" )
                except:
                    pass
                
                buff = StringIO()
                
                if img_format.upper() in [ "TIFF", "TIF" ]:
                    img.save( buff, format = img_format, compression = "raw" )
                else:
                    img.save( buff, format = img_format )
                
                buff.seek( 0 )
                file_data = buff.getvalue()
                
                if upload_type in [ "tenprint_card_front", "tenprint_card_back" ]:
                    current_app.logger.debug( "Creation of the thumbnail" )
                    utils.images.create_thumbnail( file_uuid, img, submission_uuid )
            
            else:
                file_data = fp.getvalue()
            
            file_data_r = file_data
            file_data = base64.b64encode( file_data )
            
            sql = "SELECT id FROM files_type WHERE name = %s"
            upload_type_id = config.db.query_fetchone( sql, ( upload_type, ) )[ "id" ]
            
            ####################################################################
            
            if upload_type == "consent_form":
                current_app.logger.info( "Processing of the consent form" )
                
                sql = "SELECT email_aes FROM submissions WHERE uuid = %s"
                email = config.db.query_fetchone( sql, ( submission_uuid, ) )[ "email_aes" ]
                email = utils.encryption.do_decrypt_user_session( email )
                
                sql = """
                    SELECT
                        users.username,
                        users.email
                    FROM users
                    LEFT JOIN account_type ON users.type = account_type.id
                    WHERE account_type.name = 'Donor'
                    ORDER BY users.id DESC
                """
                for username_db, email_db in config.db.query_fetchall( sql ):
                    if utils.hash.pbkdf2( email ).verify( email_db ):
                        username = username_db
                        url_hash = hashlib.sha512( email_db ).hexdigest()
                        current_app.logger.info( "Donor: {}".format( username ) )
                        break
                
                else:
                    current_app.logger.error( "User not found" )
                    return jsonify( {
                        "error": True,
                        "message": "user not found"
                    } )
                
                # Check that the PDF contains the QRCODE
                qrcode_checked = False
                
                try:
                    pages = pdf2image.convert_from_bytes( 
                        file_data_r,
                        poppler_path = config.POPPLER_PATH
                    )
                    
                    for page in pages:
                        try:
                            decoded = pyzbar.decode( page )
                            for d in decoded:
                                if d.data == "ICNML CONSENT FORM":
                                    qrcode_checked = True
                                    break
                            
                        except:
                            continue
                
                except:
                    pass
                
                # Email for the donor
                current_app.logger.info( "Sending the email to the donor" )
                email_content = utils.template.render_jinja_html( 
                    "templates/email", "donor.html",
                    username = username,
                    url = "https://icnml.unil.ch" + url_for( "newuser.config_new_user_donor", h = url_hash )
                )
                
                msg = MIMEMultipart()
                
                msg[ "Subject" ] = "ICNML - You have been added as donor"
                msg[ "From" ] = config.sender
                msg[ "To" ] = email
                
                msg.attach( MIMEText( email_content, "html" ) )
                
                part = MIMEApplication( file_data_r, Name = "consent_form.pdf" )
                part[ "Content-Disposition" ] = "attachment; filename=consent_form.pdf"
                msg.attach( part )
                 
                try:
                    with utils.mail.mySMTP() as s:
                        s.sendmail( config.sender, [ email ], msg.as_string() )
                    
                    current_app.logger.info( "Email sended" )
                
                except:
                    current_app.logger.error( "Can not send the email to the donor" )
                    return jsonify( {
                        "error": True,
                        "message": "Can not send the email to the user"
                    } )
                
                else:
                    # Consent form save
                    current_app.logger.info( "Saving the consent form to the database" )
                    file_data = config.gpg.encrypt( file_data, *config.gpg_key )
                    file_data = str( file_data )
                    file_data = base64.b64encode( file_data )
                    
                    email_hash = utils.hash.pbkdf2( email, iterations = config.CF_NB_ITERATIONS ).hash()
                    
                    sql = utils.sql.sql_insert_generate( "cf", [ "uuid", "data", "email", "has_qrcode" ] )
                    data = ( file_uuid, file_data, email_hash, qrcode_checked, )
                    config.db.query( sql , data )
                    
                    sql = "UPDATE submissions SET consent_form = true WHERE uuid = %s"
                    config.db.query( sql, ( submission_uuid, ) )
                    
                
            else:
                # Save the file to the database
                current_app.logger.info( "Save the file to the databse" )
                
                file_data = utils.encryption.do_encrypt_dek( file_data, submission_uuid )
                
                sql = utils.sql.sql_insert_generate( "files", [
                    "folder", "creator",
                    "filename", "type",
                    "format", "size", "width", "height", "resolution",
                    "uuid", "data"
                ] )
                data = ( 
                    submission_id, session[ "user_id" ],
                    file_name, upload_type_id,
                    img_format, file_size, width, height, res,
                    file_uuid, file_data,
                )
                config.db.query( sql, data )
                
                # Set the finger if available
                finger_name = request.form.get( "finger_name", None )
                if finger_name != None:
                    sql = utils.sql.sql_insert_generate( "mark_info", [ "uuid", "pfsp" ] )
                    config.db.query( sql, ( file_uuid, finger_name, ) )
                 
            return jsonify( {
                "error": False,
                "uuid": file_uuid
            } )

################################################################################
#    Submission of a new donor

@submission_view.route( "/submission/new" )
@utils.decorator.submission_has_access
def submission_new():
    """
        Serve the page to start a new submission (new donor).
    """
    current_app.logger.info( "Serve the new donor form" )
    return utils.template.my_render_template( "submission/user/new.html" )

@submission_view.route( "/submission/do_new", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_do_new():
    """
        Check the new donor data, and store the new submission process in the
        database.
    """
    current_app.logger.info( "Process the new donor form" )
    
    email = request.form.get( "email", False )
    email = email.lower()
    
    if email:
        # Check for duplicate base upon the email data
        sql = "SELECT id, email_hash FROM submissions WHERE submitter_id = %s"
        for case in config.db.query_fetchall( sql, ( session[ "user_id" ], ) ):
            if utils.hash.pbkdf2( email ).verify( case[ "email_hash" ] ):
                current_app.logger.error( "Email already used for an other submission ({}) by this submitter".format( case[ "id" ] ) )
                return jsonify( {
                    "error": True,
                    "message": "Email already used for an other submission. Check the list of submissions to update the corresponding one."
                } )
        
        else:
            current_app.logger.info( "Insertion of the donor to the databse" )
            # Insert the new donor
            donor_uuid = str( uuid4() )
            current_app.logger.debug( "Donor uuid: {}".format( donor_uuid ) )
            
            email_aes = utils.encryption.do_encrypt_user_session( email )
            email_hash = utils.hash.pbkdf2( email, iterations = config.EMAIL_NB_ITERATIONS ).hash()
            
            upload_nickname = request.form.get( "upload_nickname", None )
            upload_nickname = utils.encryption.do_encrypt_user_session( upload_nickname )
            submitter_id = session[ "user_id" ]
            
            status = "pending"
            
            userid = config.db.query_fetchone( "SELECT nextval( 'username_donor_seq' ) as id" )[ "id" ]
            username = "donor_{}".format( userid )
            sql = utils.sql.sql_insert_generate( "users", [ "username", "email", "type" ], "id" )
            data = ( username, email_hash, 2 )
            donor_user_id = config.db.query_fetchone( sql, data )[ "id" ]
            
            current_app.logger.debug( "Username: {}".format( username ) )
            
            dek_salt, dek, dek_check = utils.encryption.dek_generate( email = email, username = username )
            
            current_app.logger.debug( "DEK salt: {}...".format( dek_salt[ 0:10 ] ) )
            current_app.logger.debug( "DEK:      {}...".format( dek[ 0:10 ] ) )
            
            sql = utils.sql.sql_insert_generate(
                "donor_dek",
                [ "donor_name", "salt", "dek", "dek_check", "iterations", "algo", "hash" ],
                "id"
            )
            data = ( username, dek_salt, dek, dek_check, config.DEK_NB_ITERATIONS, "pbkdf2", "sha512", )
            config.db.query_fetchone( sql, data )
            
            sql = utils.sql.sql_insert_generate(
                "submissions",
                [ "uuid", "email_aes", "email_hash", "nickname", "donor_id", "status", "submitter_id" ]
            )
            data = ( donor_uuid, email_aes, email_hash, upload_nickname, donor_user_id, status, submitter_id, )
            config.db.query( sql, data )
            
            
            return jsonify( {
                "error": False,
                "id": donor_uuid
            } )
        
    else:
        current_app.logger.error( "No email provided for the submission folder" )
        return jsonify( {
            "error": True,
            "message": "Email not provided"
        } )

@submission_view.route( "/submission/<submission_id>/add_files" )
@utils.decorator.submission_has_access
def submission_upload_tenprintmark( submission_id ):
    """
        Serve the page to upload tenprint and mark images files. This page is
        not accessible if a consent form is not available in the database for
        this particular donor.
    """
    current_app.logger.info( "Upload a new file in the submission {}".format( submission_id ) )
    
    mark_information_details = get_submission_mark_information_details( submission_id )
    has_missing_segmentations = get_submission_tenprint_has_missing_segmentations( submission_id )
    has_missing_gp = get_submission_has_missing_gp( submission_id )
    tenprint_nb = len( get_submission_tenprint( submission_id ) )
    
    try:
        utils.encryption.dek_check( submission_id )
        
        sql = """
            SELECT
                email_aes as email,
                nickname,
                created_time,
                consent_form
            FROM submissions
            WHERE
                submitter_id = %s AND
                uuid = %s
        """
        user = config.db.query_fetchone( sql, ( session[ "user_id" ], submission_id, ) )
        
        if user[ "consent_form" ]:
            current_app.logger.debug( "The donor has a consent form" )
            current_app.logger.info( "Serving the add new file page" )
            
            for key in [ "email", "nickname" ]:
                user[ key ] = utils.encryption.do_decrypt_user_session( user[ key ] )
            
            return utils.template.my_render_template( 
                "submission/user/add_files.html",
                submission_id = submission_id,
                mark_information_details = mark_information_details,
                has_missing_segmentations = has_missing_segmentations,
                has_missing_gp = has_missing_gp,
                tenprint_nb = tenprint_nb,
                **user
            )
        else:
            current_app.logger.debug( "The donor dont have a consent form in the database" )
            current_app.logger.info( "Serving the consent form upload page" )
            
            return redirect( url_for( "submission.submission_consent_form", submission_id = submission_id ) )
        
    except:
        return jsonify( {
            "error": True,
            "message": "Case not found"
        } )

@submission_view.route( "/submission/<submission_id>/add_marks" )
@utils.decorator.submission_has_access
def submission_upload_mark_per_finger( submission_id ):
    """
        Serve the page to upload mark images files per finger.
    """
    current_app.logger.info( "Upload a new mark file in the submission {}".format( submission_id ) )
    
    try:
        utils.encryption.dek_check( submission_id )
        
        sql = """
            SELECT
                email_aes as email,
                nickname,
                created_time,
                consent_form
            FROM submissions
            WHERE
                submitter_id = %s AND
                uuid = %s
        """
        user = config.db.query_fetchone( sql, ( session[ "user_id" ], submission_id ) )
        
        if user[ "consent_form" ]:
            current_app.logger.debug( "The donor has a consent form" )
            current_app.logger.info( "Serving the add new file page" )
            
            for key in [ "email", "nickname" ]:
                user[ key ] = utils.encryption.do_decrypt_user_session( user[ key ] )
            
            finger_names = []
            for laterality in [ "Right", "Left" ]:
                for finger in [ "thumb", "index", "middle", "ring", "little" ]:
                    finger_names.append( "{} {}".format( laterality, finger ) )
            
            return utils.template.my_render_template( 
                "submission/user/add_marks_by_finger.html",
                submission_id = submission_id,
                finger_names = finger_names,
                user = user
            )
        else:
            current_app.logger.debug( "The donor dont have a consent form in the database" )
            current_app.logger.info( "Serving the consent form upload page" )
            
            return redirect( url_for( "submission.submission_consent_form", submission_id = submission_id ) )
        
    except:
        return jsonify( {
            "error": True,
            "message": "Case not found"
        } )

@submission_view.route( "/submission/<submission_id>/consent_form" )
@utils.decorator.submission_has_access
def submission_consent_form( submission_id ):
    """
        Serve the page to upload the consent form for the user.
    """
    current_app.logger.info( "Serve the consent form upload page" )
    
    sql = """
        SELECT
            email_aes as email,
            nickname,
            created_time
        FROM submissions
        WHERE
            submitter_id = %s AND
            uuid = %s
    """
    user = config.db.query_fetchone( sql, ( session[ "user_id" ], submission_id, ) )
    
    if user != None:
        for key in [ "email", "nickname" ]:
            user[ key ] = utils.encryption.do_decrypt_user_session( user[ key ] )
        
        return utils.template.my_render_template( 
            "submission/user/consent_form.html",
            submission_id = submission_id,
            **user
        )
    
    else:
        current_app.logger.error( "Submission not found" )
        return abort( 404 )

@submission_view.route( "/submission/<submission_id>/gp" )
@utils.decorator.submission_has_access
def submission_gp( submission_id ):
    """
        Serve the page to upload the general pattern for a donor.
    """
    current_app.logger.info( "Serve the page to set the GP for {}".format( submission_id ) )
    
    finger_names = []
    for laterality in [ "Right", "Left" ]:
        for finger in [ "thumb", "index", "middle", "ring", "little" ]:
            finger_names.append( "{} {}".format( laterality, finger ) )
    
    gp_list = [
        {
            "div_name": "ll",
            "name": "left loop"
        },
        {
            "div_name": "rl",
            "name": "right loop"
        },
        {
            "div_name": "whorl",
            "name": "whorl"
        },
        {
            "div_name": "arch",
            "name": "arch"
        },
        {
            "div_name": "cpl",
            "name": "central pocket loop"
        },
        {
            "div_name": "dl",
            "name": "double loop"
        },
        {
            "div_name": "ma",
            "name": "missing/amputated"
        },
        {
            "div_name": "sm",
            "name": "scarred/mutilated"
        },
        {
            "div_name": "unknown",
            "name": "unknown"
        }
    ]
    
    try:
        sql = """
            SELECT
                donor_fingers_gp.fpc,
                gp.div_name,
                gp.name
            FROM donor_fingers_gp
            LEFT JOIN submissions ON donor_fingers_gp.donor_id = submissions.donor_id
            LEFT JOIN gp ON donor_fingers_gp.gp = gp.id
            WHERE
                submissions.uuid = %s AND
                donor_fingers_gp.fpc <= 10
            ORDER BY donor_fingers_gp.fpc ASC
        """
        current_gp = config.db.query_fetchall( sql, ( submission_id, ) )
        
        utils.encryption.dek_check( submission_id )
        
        sql = """
            SELECT
                email_aes as email,
                nickname,
                created_time,
                consent_form
            FROM submissions
            WHERE
                submitter_id = %s AND
                uuid = %s
        """
        user = config.db.query_fetchone( sql, ( session[ "user_id" ], submission_id, ) )
        
        for key in [ "email", "nickname" ]:
            user[ key ] = utils.encryption.do_decrypt_user_session( user[ key ] )
        
        return utils.template.my_render_template( 
            "submission/user/set_gp.html",
            submission_id = submission_id,
            finger_names = finger_names,
            gp_list = gp_list,
            current_gp = current_gp,
            user = user
        )
    
    except:
        return jsonify( {
            "error": True,
            "message": "Case not found"
        } )

@submission_view.route( "/submission/<submission_id>/set/nickname", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_update_nickname( submission_id ):
    """
        Change the nickname of the donor in the database.

        THIS INFORMATION SHALL BE ENCRYPTED ON THE CLIENT SIDE FIRST WITH A
        UNIQUE ENCRYPTION KEY NOT TRANSMITTED TO THE SERVER!
    """
    current_app.logger.info( "Save the donor nickname to the database" )
    
    nickname = request.form.get( "nickname", None )
    
    if nickname != None and len( nickname ) != 0:
        try:
            nickname = utils.encryption.do_encrypt_user_session( nickname )
            
            sql = """
                UPDATE submissions
                SET nickname = %s
                WHERE uuid = %s
            """
            config.db.query( sql, ( nickname, submission_id, ) )
            
            return jsonify( {
                "error": False
            } )
        
        except:
            current_app.logger.error( "Database error" )
            return jsonify( {
                "error": True,
                "message": "DB error"
            } )
    
    else:
        current_app.logger.error( "No nickname in the post request" )
        return jsonify( {
            "error": True,
            "message": "No new nickname in the POST request"
        } )

@submission_view.route( "/submission/list" )
@utils.decorator.submission_has_access
def submission_list():
    """
        Get the list of all submissions folder for the currently logged
        submitter.
    """
    current_app.logger.info( "Get all submissions for '{}'".format( session[ "username" ] ) )
    
    @utils.redis.redis_cache( 10 )
    def tmp_get_submission_list():
        sql = """
            SELECT
                nickname, uuid, id, f
            FROM submissions
            LEFT JOIN (
                SELECT
                    DISTINCT ON ( folder )
                    folder, uuid AS f
                FROM files
                ORDER BY folder, id ASC
            ) AS tmpfiles ON tmpfiles.folder = submissions.id
            WHERE submitter_id = %s
            ORDER BY created_time DESC
        """
        return config.db.query_fetchall( sql, ( session[ "user_id" ], ) )
    
    donors = tmp_get_submission_list()
    
    for _, d in enumerate( donors ):
        d[ "nickname" ] = utils.encryption.do_decrypt_user_session( d[ "nickname" ] )

    current_app.logger.info( "{} submissions found".format( len( donors ) ) )
    
    return utils.template.my_render_template(
        "submission/user/list.html",
        donors = donors
    )

@submission_view.route( "/admin/submission/<submission_id>/mark/list" )
@submission_view.route( "/admin/submission/<submission_id>/mark/list/<mark_type>" )
@utils.decorator.submission_has_access
def admin_submission_mark_list( submission_id, mark_type = "all" ):
    """
        Serve the list of marks for admins. See the
        `submission_mark_list_inner` function for more details.
    """
    return submission_mark_list_inner( submission_id, mark_type, True )

@submission_view.route( "/submission/<submission_id>/mark/list" )
@submission_view.route( "/submission/<submission_id>/mark/list/<mark_type>" )
@utils.decorator.submission_has_access
def submission_mark_list( submission_id, mark_type = "all" ):
    """
        Serve the list of marks for submitters. See the
        `submission_mark_list_inner` function for more details.
    """
    return submission_mark_list_inner( submission_id, mark_type, False )

def submission_mark_list_inner( submission_id, mark_type, admin ):
    """
        Get the list of mark for a particular submission folder.
    """
    info_fields = [ "pfsp", "detection_technic", "surface" ]
    
    current_app.logger.info( "Get the list of mark for the submission '{}'".format( submission_id ) )
    current_app.logger.debug( "mark_type: {}".format( mark_type ) )
    
    if mark_type in [ "target", "incidental", "all" ]:
        sql = """
            SELECT
                submissions.id,
                submissions.nickname,
                users.username
            FROM submissions
            INNER JOIN users ON submissions.donor_id = users.id
            WHERE uuid = %s
        """
        case_id, nickname, username = config.db.query_fetchone( sql, ( submission_id, ) )
        if admin:
            displayed_name = username
        else:
            displayed_name = utils.encryption.do_decrypt_user_session( nickname )
        
        sql = """
            SELECT
                files.id,
                files.uuid,
                files.filename,
                files.size,
                files.creation_time,
        """
        
        sql += ",".join( [ "mark_info.{}".format( field ) for field in info_fields ] )
        
        sql += """
            FROM files
            LEFT JOIN files_type ON files.type = files_type.id
            LEFT JOIN mark_info ON files.uuid = mark_info.uuid
            WHERE folder = %s
        """
        if mark_type == "target":
            sql += " AND files_type.name = 'mark_target'"
        elif mark_type == "incidental":
            sql += " AND files_type.name = 'mark_incidental'"
        elif mark_type == "all":
            sql += " AND ( files_type.name = 'mark_target' OR files_type.name = 'mark_incidental' )"
        
        sql += " ORDER BY files.id DESC"
        files = config.db.query_fetchall( sql, ( case_id, ) )
        
        for _, v in enumerate( files ):
            v[ "filename" ] = utils.encryption.do_decrypt_user_session( v[ "filename" ] )
            v[ "size" ] = round( ( float( v[ "size" ] ) / ( 1024 * 1024 ) ) * 100 ) / 100
            
            for e in info_fields:
                v[ e ] = v[ e ] == None or v[ e ] == "{}"
            
        current_app.logger.debug( "{} marks for '{}'".format( len( files ), submission_id ) )
        
        return utils.template.my_render_template( 
            "submission/shared/mark_list.html",
            info_fields = info_fields,
            submission_id = submission_id,
            mark_type = mark_type,
            files = files,
            displayed_name = displayed_name
        )
    
    else:
        return abort( 403 )

@utils.redis.redis_cache( 10 )
def get_submission_mark_information_details( submission_id ):
    """
        Get the list of all informations related to a mark (position, detection
        technic, suface, ...).
    """
    def get_sql_missing_information( file_type_name, check_type ):
        info_fields = [ "pfsp", "detection_technic", "surface" ]
        if check_type == "missing":
            empty_fields_where = " OR ".join( [ "{} IS NULL".format( f ) for f in info_fields ] )
        else:
            empty_fields_where = " AND ".join( [ "{} IS NOT NULL".format( f ) for f in info_fields ] )
        
        sql = """
            SELECT count(*) AS nb
            FROM files
            LEFT JOIN submissions ON files.folder = submissions.id
            LEFT JOIN files_type ON files.type = files_type.id
            LEFT JOIN mark_info ON files.uuid = mark_info.uuid
            WHERE
                submissions.uuid = %s AND
                files_type.name = '{}' AND
                ( {} )
        """.format( file_type_name, empty_fields_where )
        return sql
    
    ret = {}
    for mark_type in [ "mark_incidental", "mark_target" ]:
        ret[ mark_type ] = {}
        
        tot = 0
        for check_type in [ "missing", "complete" ]:
            sql = get_sql_missing_information( mark_type, check_type )
            query = config.db.query_fetchone( sql, ( submission_id, ) )
            nb = query[ "nb" ]
            
            tot += nb
            
            ret[ mark_type ][ check_type ] = nb
        ret[ mark_type ][ "total" ] = tot
        
    return ret

@utils.redis.redis_cache( 10 )
def get_submission_mark_has_missing_information( submission_id, mark_type_list = None ):
    """
        Check if the mark mask missing information. This check is done for
        incidental and target marks.
    """
    i = get_submission_mark_information_details( submission_id )
    
    if mark_type_list == None:
        mark_type_list = [ "mark_incidental", "mark_target" ]
    elif not isinstance( mark_type_list, ( list, tuple ) ):
        mark_type_list = [ mark_type_list ]
        
    for mark_type in mark_type_list:
        if i[ mark_type ][ 'missing' ] > 0:
            return True
    else:
        return False

@utils.redis.redis_cache( 10 )
def get_submission_tenprint( submission_id ):
    """
        Get the list of tenprint cards related to a submission.
    """
    sql = """
        SELECT
            files.uuid,
            files_type.name
        FROM submissions
        LEFT JOIN files ON submissions.id = files.folder
        LEFT JOIN files_type ON files.type = files_type.id
        WHERE
            submissions.uuid = %s AND
            (
                files_type.name = 'tenprint_card_back' OR
                files_type.name = 'tenprint_card_front' OR
                files_type.name = 'tenprint_nist'
            )
    """
    return config.db.query_fetchall( sql, ( submission_id, ) )

@utils.redis.redis_cache( 10 )
def get_submission_tenprint_segments_count( submission_id ):
    """
        Get the number of segments annotated for each tenprint card related to
        a submission id.
    """
    ret = []
    
    for file in get_submission_tenprint( submission_id ):
        sql = "SELECT count(*) FROM segments_locations WHERE tenprint_id = %s"
        nb = config.db.query_fetchone( sql, ( file[ 'uuid' ], ) )[ "count" ]
        ret.append( {
            'uuid': file[ 'uuid' ],
            'type': file[ 'name' ],
            'nb': nb
        } )
        
    return ret
    
@utils.redis.redis_cache( 10 )
def get_submission_tenprint_has_missing_segmentations( submission_id ):
    """
        Check if a submission has missing segments. This check is done on all
        tenprint cards related to the submission folder.
    """
    for s in get_submission_tenprint_segments_count( submission_id ):
        if s[ 'nb' ] == 0:
            return True
    else:
        return False
    
@utils.redis.redis_cache( 10 )
def get_submission_has_missing_gp( submission_id ):
    """
        Check if the submission has the general pattern set.
    """
    sql = """
        SELECT count(*)
        FROM donor_fingers_gp
        LEFT JOIN submissions ON donor_fingers_gp.donor_id = submissions.donor_id
        WHERE
            submissions.uuid = %s
    """
    nb = config.db.query_fetchone( sql, ( submission_id, ) )[ "count" ]
    return nb < 10

@utils.redis.redis_cache( 10 )
def get_submission_has_no_tenprint( submission_id ):
    """
        Check if the submission has tenprint cards uploaded or not.
    """
    lst = get_submission_tenprint( submission_id )
    return len( lst ) == 0

@submission_view.route( "/admin/submission/<submission_id>/missing_information" )
@utils.decorator.login_required
def get_submission_missing_information_all( submission_id ):
    """
        Check for all missing information related to a submission.
    """
    admin = session.get( "account_type_name", None ) == "Administrator"
    
    try:
        def info_get( sid ):
            mark_has_missing_information = get_submission_mark_has_missing_information( sid )
            has_missing_segmentations = get_submission_tenprint_has_missing_segmentations( sid )
            has_missing_gp = get_submission_has_missing_gp( sid )
            has_no_tp = get_submission_has_no_tenprint( sid )
            return mark_has_missing_information or has_missing_segmentations or has_missing_gp or has_no_tp
        
        if submission_id != "all":
            data = info_get( submission_id )
        
        else:
            if admin:
                sql = "SELECT uuid FROM submissions"
                params = ()
            else:
                sql = "SELECT uuid FROM submissions WHERE submitter_id = %s"
                params = ( session.get( "user_id" ), )
                
            data = []
            for donor in config.db.query_fetchall( sql, params ):
                missing = info_get( donor[ 'uuid' ] )
                if missing:
                    data.append( donor[ 'uuid' ] )
        
        return jsonify( {
            'error': False,
            'data': data
        } )
    
    except:
        return jsonify( {
            'error': True
        } )

@submission_view.route( "/submission/<submission_id>/targets" )
@utils.decorator.submission_has_access
def donor_marks_annotations( submission_id ):
    """
        Serve the page for targets area for users.
    """
    
    sql = """
        SELECT
            nickname
        FROM submissions
        WHERE uuid = %s
    """
    nickname = config.db.query_fetchone( sql, ( submission_id, ) )[ "nickname" ]
    nickname = utils.encryption.do_decrypt_user_session( nickname )
    
    sql = """
        SELECT
            cnm_annotation.id,
            cnm_annotation.uuid,
            cnm_folder.pc AS fpc
        FROM cnm_annotation
        LEFT JOIN cnm_folder ON cnm_annotation.folder_uuid = cnm_folder.uuid
        LEFT JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
        WHERE
            submissions.uuid = %s
        ORDER BY cnm_folder.pc ASC
    """
    annotations = config.db.query_fetchall( sql, ( submission_id, ) )
    
    return utils.template.my_render_template(
        "submission/user/target.html",
        submission_id = submission_id,
        nickname = nickname,
        annotations = annotations,
        segments_position_code = segments_position_code
    )

@submission_view.route( "/submission/<submission_id>/mark/<mark_id>/set/pfsp", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_mark_pfsp_set( submission_id, mark_id ):
    """
        Save the PFSP information relative to a mark.
    """
    current_app.logger.info( "Save the PFSP for submission '{}' mark '{}'".format( submission_id, mark_id ) )
    
    try:
        pfsp = request.form.get( "pfsp" )
        pfsp = ",".join( [ p for p in pfsp.split( "," ) if p != "None" ] )
        
        sql = "SELECT id FROM mark_info WHERE uuid = %s"
        q = config.db.query_fetchone( sql, ( mark_id, ) )
        
        if q == None:
            sql = utils.sql.sql_insert_generate( "mark_info", [ "uuid", "pfsp" ] )
            config.db.query( sql, ( mark_id, pfsp, ) )
        
        else:
            sql = "UPDATE mark_info SET pfsp = %s WHERE uuid = %s"
            config.db.query( sql, ( pfsp, mark_id, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/mark/<mark_id>/set/<field>", methods = [ "POST" ] )
@submission_view.route( "/submission/<submission_id>/mark/<mark_id>/set", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_mark_set_field( submission_id, mark_id, field = None ):
    """
        Set the data related to the <field> (detection technic, surface, ...)
        for a fingermark.
    """
    corr = {
        "surface": "surface",
        "detection": "detection_technic",
        "activity": "activity",
        "distortion": "distortion"
    }
    if field == None:
        field = request.form.get( "field" )
    field = corr.get( field, False )
    
    if field != False:
        current_app.logger.info( "Save the {} for submission '{}' mark '{}'".format( field, submission_id, mark_id ) )
        
        dt = request.form.get( "value", None )
        if dt == "":
            dt = None
        
        sql = "SELECT id FROM mark_info WHERE uuid = %s"
        q = config.db.query_fetchone( sql, ( mark_id, ) )
        
        if q == None:
            sql = utils.sql.sql_insert_generate( "mark_info", [ "uuid", field ] )
            config.db.query( sql, ( mark_id, dt, ) )
        
        else:
            sql = "UPDATE mark_info SET {} = %s WHERE uuid = %s".format( field )
            config.db.query( sql, ( dt, mark_id, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    else:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/mark/<mark_id>/delete" )
@submission_view.route( "/submission/<submission_id>/mark/delete", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_mark_delete( submission_id, mark_id = None ):
    """
        Delete a mark from a submission folder for users. See the
        `submission_mark_delete_inner` function.
    """
    if mark_id == None:
        mark_id = request.form.get( "mark_id" )
        
    return submission_mark_delete_inner( submission_id, mark_id, False )

@submission_view.route( "/admin/submission/<submission_id>/mark/<mark_id>/delete" )
@submission_view.route( "/admin/submission/<submission_id>/mark/delete", methods = [ "POST" ] )
@utils.decorator.admin_required
def admin_submission_mark_delete( submission_id, mark_id = None ):
    """
        Delete a mark from a submission folder for admins. See the
        `submission_mark_delete_inner` function.
    """
    if mark_id == None:
        mark_id = request.form.get( "mark_id" )
        
    return submission_mark_delete_inner( submission_id, mark_id, True )

def submission_mark_delete_inner( submission_id, mark_id, admin ):
    """
        Delete a mark from the database.
    """
    current_app.logger.info( "Delete mark '{}' from submission '{}'".format( mark_id, submission_id ) )
    
    try:
        if admin:
            sql = "DELETE FROM files WHERE uuid = %s"
            data = ( mark_id, )
        else:
            sql = "DELETE FROM files WHERE creator = %s AND uuid = %s"
            data = ( session[ "user_id" ], mark_id, )
            
        config.db.query( sql, data )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

################################################################################
#    Submission deletion

@submission_view.route( "/submission/<submission_id>/delete" )
@utils.decorator.submission_has_access
def submission_delete( submission_id ):
    """
        Delete the empty submission. A submission can not be deleted after the
        upload of the consent form and the creation of the donor user.
    """
    current_app.logger.info( "Delete the submission '{}' for user '{}'".format( submission_id, session[ "username" ] ) )
    
    sql = "SELECT consent_form FROM submissions WHERE submitter_id = %s AND uuid = %s"
    cf = config.db.query_fetchone( sql, ( session[ "user_id" ], submission_id, ) )[ "consent_form" ]
    
    if not cf:
        sql = "DELETE FROM submissions WHERE submitter_id = %s AND uuid = %s"
        config.db.query( sql, ( session[ "user_id" ], submission_id, ) )
        
        return jsonify( {
            "error": False
        } )
    
    else:
        current_app.logger.error( "Can  not delete a submission with consent form" )
        return jsonify( {
            "error": True,
            "message": "Can not delete if a consent form is already uploaded"
        } )

@submission_view.route( "/submission/<submission_id>/tenprint/list" )
@utils.decorator.submission_has_access
def submission_tenprint_list( submission_id ):
    """
        Serve the page with the list of tenprint images, split by front, back
        and NIST format.
    """
    current_app.logger.info( "Get the list of tenprint for the submission '{}'".format( submission_id ) )
    sql = "SELECT id, nickname FROM submissions WHERE uuid = %s"
    submission_folder_id, nickname = config.db.query_fetchone( sql, ( submission_id, ) )
    nickname = utils.encryption.do_decrypt_user_session( nickname )
    
    sql = """
        SELECT
            id, uuid,
            filename, type,
            creation_time
        FROM files
        WHERE
            folder = %s AND
            ( type = 1 OR type = 2 OR type = 5 )
        ORDER BY creation_time DESC
    """
    tenprint_cards = config.db.query_fetchall( sql, ( submission_folder_id, ) )
    
    for _, tenprint in enumerate( tenprint_cards ):
        tenprint[ 'filename' ] = utils.encryption.do_decrypt_user_session( tenprint[ "filename" ] )
    
    segments = get_submission_tenprint_segments_count( submission_id )
    
    return utils.template.my_render_template( 
        "submission/user/tenprint_list.html",
        tenprint_cards = tenprint_cards,
        submission_id = submission_id,
        nickname = nickname,
        segments = segments
    )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>" )
@utils.decorator.submission_has_access
def submission_tenprint( submission_id, tenprint_id ):
    """
        Serve the page to see and edit a tenprint file.
    """
    current_app.logger.info( "Serve tenprint edit page for '{}', submission '{}'".format( tenprint_id, submission_id ) )
    sql = "SELECT id, nickname FROM submissions WHERE uuid = %s"
    submission_folder_id, nickname = config.db.query_fetchone( sql, ( submission_id, ) )
    nickname = utils.encryption.do_decrypt_user_session( nickname )
    
    sql = """
        SELECT
            files.uuid, files.filename, files.note,
            files.format, files.resolution, files.width, files.height, files.size,
            files.creation_time, files.type,
            files.quality
        FROM files
        WHERE
            folder = %s AND
            files.uuid = %s
    """
    
    tenprint_file = config.db.query_fetchone( sql, ( submission_folder_id, tenprint_id, ) )
    
    current_app.logger.debug( "tenprint type: {}".format( tenprint_file[ "type" ] ) )
    
    if tenprint_file[ "type" ] == 5:
        current_app.logger.debug( "Redirect to the segments list page" )
        return redirect( url_for( "submission.tenprint_segments_list", submission_id = submission_id, tenprint_id = tenprint_id ) )
    
    else:
        tenprint_file[ "size" ] = round( 100 * float( tenprint_file[ "size" ] ) / ( 1024 * 1024 ) ) / 100
        tenprint_file[ "filename" ] = utils.encryption.do_decrypt_user_session( tenprint_file[ "filename" ] )
        
        if tenprint_file[ "type" ] == 1:
            side = "front"
        elif tenprint_file[ "type" ] == 2:
            side = "back"
        
        ############################################################################
        
        sql = "SELECT id, name FROM quality_type"
        quality_type = config.db.query_fetchall( sql )
        
        ############################################################################
        
        sql = "SELECT width, height, resolution FROM files WHERE uuid = %s LIMIT 1"
        img_info = config.db.query_fetchone( sql, ( tenprint_id, ) )
        svg_hw_factor = float( img_info[ "width" ] ) / float( img_info[ "height" ] )
        
        ############################################################################
        
        sql = "SELECT * FROM segments_locations WHERE tenprint_id = %s ORDER BY fpc ASC"
        zones_raw = config.db.query_fetchall( sql, ( tenprint_id, ) )
        zones = []
        
        for z in zones_raw:
            tmp = {}
            for k in [ "fpc", "orientation" ]:
                tmp[ k ] = z[ k ]
            
            for k in [ "x", "width" ]:
                tmp[ k ] = z[ k ] / img_info[ "width" ]
            for k in [ "y", "height" ]:
                tmp[ k ] = z[ k ] / img_info[ "height" ]
            
            zones.append( tmp )
        
        ############################################################################
        
        if side == "front":
            to_annotate = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ]
        else:
            to_annotate = [ 25, 27, 22, 24 ]
        
        ############################################################################
        
        return utils.template.my_render_template( 
            "submission/shared/tenprint.html",
            segments_position_code = segments_position_code,
            to_annotate = to_annotate,
            submission_id = submission_id,
            file = tenprint_file,
            nickname = nickname,
            img_info = img_info,
            zones = zones,
            svg_hw_factor = svg_hw_factor,
            quality_type = quality_type
        )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/delete" )
@utils.decorator.submission_has_access
def submission_tenprint_delete( submission_id, tenprint_id ):
    """
        Endpoint to delete a tenprint image.
    """
    current_app.logger.info( "Delete tenprint '{}' from submission '{}'".format( tenprint_id, submission_id ) )
    
    try:
        sql = "DELETE FROM files WHERE uuid = %s"
        config.db.query( sql, ( tenprint_id, ) )
        
        sql = "DELETE FROM files_segments WHERE tenprint = %s"
        config.db.query( sql, ( tenprint_id, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/set/template", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_tenprint_set_template( submission_id, tenprint_id ):
    """
        Set the template id for a tenprint image.
    """
    try:
        template = request.form.get( "template" )
        current_app.logger.info( "Set tenprint template id to '{}' for '{}', submission id '{}'".format( template, tenprint_id, submission_id ) )
        
        sql = "SELECT id FROM file_template WHERE file = %s"
        q = config.db.query_fetchone( sql, ( tenprint_id, ) )
        
        if q == None:
            sql = utils.sql.sql_insert_generate( "file_template", [ "file", "template" ] )
            config.db.query( sql, ( tenprint_id, template, ) )
        
        else:
            sql = "UPDATE file_template SET template = %s WHERE file = %s"
            config.db.query( sql, ( template, tenprint_id, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/file/<file_uuid>/set/note", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_file_set_note( submission_id, file_uuid ):
    """
        Store the user encrypted notes for a tenprint image.
    """
    try:
        current_app.logger.info( "Add note for file '{}', submission id '{}'".format( file_uuid, submission_id ) )
        note = request.form.get( "note" )
        
        sql = "UPDATE files SET note = %s WHERE uuid = %s RETURNING id"
        config.db.query( sql, ( note, file_uuid, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/set/quality", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_tenprint_set_quality( submission_id, tenprint_id ):
    """
        Store the quality for a tenprint image.
    """
    try:
        quality = request.form.get( "quality" )
        current_app.logger.info( "Set the quality to '{}' for tenprint '{}', submission id '{}'".format( quality, tenprint_id, submission_id ) )
        
        sql = "UPDATE files SET quality = %s WHERE uuid = %s RETURNING id"
        config.db.query( sql, ( quality, tenprint_id, ) )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

################################################################################
#    Tenprint segments

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/segment/list" )
@utils.decorator.submission_has_access
def submission_tenprint_segments_list( submission_id, tenprint_id ):
    """
        Serve the page with the list of segments for a tenprint image.
    """
    current_app.logger.info( "Get the list of segments for tenprint '{}', submission id '{}'".format( tenprint_id, submission_id ) )
    sql = """
        SELECT
            id,
            nickname
        FROM submissions
        WHERE uuid = %s
    """
    submission_folder_id, nickname = config.db.query_fetchone( sql, ( submission_id, ) )
    nickname = utils.encryption.do_decrypt_user_session( nickname )
    
    sql = """
        SELECT
            uuid,
            filename
        FROM files
        WHERE
            folder = %s AND
            files.uuid = %s
    """
    
    tenprint_file = config.db.query_fetchone( sql, ( submission_folder_id, tenprint_id, ) )
    filename = utils.encryption.do_decrypt_user_session( tenprint_file[ "filename" ] )
    tenprint_id = tenprint_file[ "uuid" ]
    
    ############################################################################
    
    sql = """
        SELECT
            files_segments.pc,
            files_segments.data,
            pc.name
        FROM files_segments
        LEFT JOIN pc ON pc.id = files_segments.pc
        WHERE tenprint = %s
    """
    segments = config.db.query_fetchall( sql, ( tenprint_id, ) )
    nb_segments = len( segments )
    
    current_app.logger.debug( "{} segments stored in database".format( nb_segments ) )
    
    ############################################################################
    
    return utils.template.my_render_template( 
        "submission/user/segment_list.html",
        submission_id = submission_id,
        tenprint_id = tenprint_id,
        nickname = nickname,
        filename = filename,
        segments = segments,
        nb_segments = nb_segments
    )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/segment/<pc>" )
@utils.decorator.submission_has_access
def submission_segment( submission_id, tenprint_id, pc ):
    """
        Serve the page to edit the information relative to a segment image.
    """
    current_app.logger.info( "Serve the edit page for segment '{}'".format( pc ) )
    
    pc = int( pc )
    
    if not pc in config.all_fpc:
        current_app.logger.error( "'{}' not in the pc_list".format( pc ) )
        return redirect( url_for( "submission.tenprint_segments_list", submission_id = submission_id, tenprint_id = tenprint_id ) )
    
    else:
        current_app.logger.debug( "Retrieving data for submission '{}', pc '{}'".format( submission_id, pc ) )
        
        sql = """
            SELECT
                id,
                nickname
            FROM submissions
            WHERE uuid = %s
        """
        submission_folder_id, nickname = config.db.query_fetchone( sql, ( submission_id, ) )
        nickname = utils.encryption.do_decrypt_user_session( nickname )
        
        sql = """
            SELECT
                uuid,
                filename,
                type
            FROM files
            WHERE
                folder = %s AND
                files.uuid = %s
        """
        tp_file = config.db.query_fetchone( sql, ( submission_folder_id, tenprint_id, ) )
        tp_filename = utils.encryption.do_decrypt_user_session( tp_file[ "filename" ] )
        
        sql = "SELECT name FROM pc WHERE id = %s"
        pc_name = config.db.query_fetchone( sql, ( pc, ) )[ "name" ]
        
        sql = """
            SELECT gp.div_name
            FROM donor_fingers_gp
            LEFT JOIN submissions ON donor_fingers_gp.donor_id = submissions.donor_id
            LEFT JOIN gp ON donor_fingers_gp.gp = gp.id
            WHERE submissions.uuid = %s AND donor_fingers_gp.fpc = %s
        """
        try:
            current_gp = config.db.query_fetchone( sql, ( submission_id, pc, ) )[ "div_name" ]
        except:
            current_gp = None
        
        if pc in xrange( 1, 10 ):
            next_pc = pc + 1
            tp_type = "finger"
        elif pc == 10:
            next_pc = None
            tp_type = "finger"
        elif pc == 25:
            next_pc = 27
            tp_type = "palm"
        elif pc == 27:
            next_pc = None
            tp_type = "palm"
        else:
            return abort( 404 )
        
        current_app.logger.debug( "pc: {}".format( pc ) )
        current_app.logger.debug( "tp_type: {}".format( tp_type ) )
        current_app.logger.debug( "next pc: {}".format( next_pc ) )
        
        return utils.template.my_render_template( 
            "submission/user/segment.html",
            submission_id = submission_id,
            nickname = nickname,
            pc_name = pc_name,
            tp_filename = tp_filename,
            tenprint_id = tenprint_id,
            pc = pc,
            next_pc = next_pc,
            current_gp = current_gp,
            tp_type = tp_type
        )

@submission_view.route( "/submission/<submission_id>/tenprint/segment/<pc>/set/gp", methods = [ "POST" ] )
@submission_view.route( "/submission/<submission_id>/tenprint/segment/set/gp", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_segment_set_gp( submission_id, pc = None ):
    """
        Set the general pattern of a fingerprint segment image (FPC 1-10).
    """
    try:
        if pc == None:
            pc = request.form.get( "pc" )
        
        pc = int( pc )
        
        gp = request.form.get( "gp" )
        
        current_app.logger.info( "Set general pattern for '{}', pc '{}' to '{}'".format( submission_id, pc, gp ) )
        
        sql = """
            SELECT id
            FROM gp
            WHERE
                name = %s OR
                div_name = %s
        """
        r = config.db.query_fetchone( sql, ( gp, gp, ) )
        if r == None:
            current_app.logger.error( "General pattern not recognized" )
            return jsonify( {
                "error": True,
                "message": "General pattern not recognized"
            } )
        
        gp_id = r[ "id" ]
        
        sql = """
            SELECT
                count( * )
            FROM donor_fingers_gp
            LEFT JOIN submissions ON donor_fingers_gp.donor_id = submissions.donor_id
            WHERE
                submissions.uuid = %s AND
                donor_fingers_gp.fpc = %s
            GROUP BY donor_fingers_gp.id
        """
        nb = config.db.query_fetchone( sql, ( submission_id, pc, ) )
        
        sql = "SELECT donor_id FROM submissions WHERE uuid = %s"
        donor_id = config.db.query_fetchone( sql, ( submission_id, ) )[ "donor_id" ]
        
        if nb == 0 or nb == None:
            current_app.logger.debug( "Insert general pattern in database" )
            sql = utils.sql.sql_insert_generate( "donor_fingers_gp", [ "donor_id", "fpc", "gp" ] )
            config.db.query( sql, ( donor_id, pc, gp_id, ) )
        
        else:
            current_app.logger.debug( "Update general patern in database" )
            sql = "UPDATE donor_fingers_gp SET gp = %s WHERE donor_id = %s AND fpc = %s"
            config.db.query( sql, ( gp_id, donor_id, pc, ) )
        
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/segment/set_coordinates", methods = [ "POST" ] )
@utils.decorator.submission_has_access
def submission_segment_setcoordinates( submission_id, tenprint_id ):
    """
        Add the segment location data to the database.
    """
    try:
        fpc = request.form.get( "fpc" )
        x = float( request.form.get( "x" ) )
        y = float( request.form.get( "y" ) )
        w = float( request.form.get( "w" ) )
        h = float( request.form.get( "h" ) )
        img_width = float( request.form.get( "img_width" ) )
        img_height = float( request.form.get( "img_height" ) )
        orientation = int( request.form.get( "orientation" ) )
        
        img_data = views.images.do_img_info( tenprint_id )
        
        fpc = int( fpc )
        
        x_seg = int( x / img_width * img_data[ "width" ] )
        y_seg = int( y / img_height * img_data[ "height" ] )
        
        width_seg = int( w / img_width * img_data[ "width" ] )
        height_seg = int( h / img_height * img_data[ "height" ] )
        
        sql = """
            SELECT count( * )
            FROM segments_locations
            WHERE
                tenprint_id = %s AND
                fpc = %s
        """
        count = config.db.query_fetchone( sql, ( tenprint_id, fpc, ) )[ "count" ]
        
        if count == 0:
            sql = utils.sql.sql_insert_generate(
                "segments_locations",
                [ "tenprint_id", "fpc", "x", "y", "width", "height", "orientation" ],
                "id"
            )
            data = ( tenprint_id, fpc, x_seg, y_seg, width_seg, height_seg, orientation, )
            seg_data_id = config.db.query_fetchone( sql, data )[ "id" ]
        
        else:
            sql = """
                UPDATE segments_locations
                SET
                    x = %s,
                    y = %s,
                    width = %s,
                    height = %s,
                    orientation = %s
                WHERE
                    tenprint_id = %s AND
                    fpc = %s
                RETURNING id
            """
            data = ( x_seg, y_seg, width_seg, height_seg, orientation, tenprint_id, fpc, )
            seg_data_id = config.db.query_fetchone( sql, data )[ "id" ]
        
        
        return jsonify( {
            "error": False,
            "id": seg_data_id,
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/segment/delete_coordinates", methods = [ "GET", "POST" ] )
@submission_view.route( "/submission/<submission_id>/tenprint/<tenprint_id>/segment/delete_coordinates/<fpc>" )
@utils.decorator.submission_has_access
def submission_segment_deletecoordinates( submission_id, tenprint_id, fpc = None ):
    """
        Delete all segment information for a particular submission finger.
    """
    try:
        if fpc == None:
            fpc = request.form.get( "pc", "all" )
        
        if fpc == "all":
            sql = "DELETE FROM segments_locations WHERE tenprint_id = %s"
            data = ( tenprint_id, )
        
        else:
            fpc = int( fpc )
            if fpc in config.all_fpc:
                sql = "DELETE FROM segments_locations WHERE tenprint_id = %s AND fpc = %s"
                data = ( tenprint_id, int( fpc ), )
            else:
                raise Exception( "fpc not valid" )
            
        config.db.query( sql, data )
        
        return jsonify( {
            "error": False
        } )
    
    except:
        return jsonify( {
            "error": True
        } )

################################################################################
#    Admin review

@submission_view.route( "/admin/<submission_id>" )
@utils.decorator.admin_required
def admin_submission_home( submission_id ):
    """
        Get the admin view for a submission. From this homepage, the user can
        open any themed pages (tenprint cards, marks, target area, ...).
    """
    sql = """
        SELECT
            submissions.id,
            submissions.uuid,
            donor_join.username AS donor_username,
            submitter_join.username AS submitter_username
        FROM submissions
        LEFT JOIN users AS donor_join     ON submissions.donor_id = donor_join.id
        LEFT JOIN users AS submitter_join ON submissions.submitter_id = submitter_join.id
        WHERE submissions.uuid = %s
    """
    submission = config.db.query_fetchone( sql, ( submission_id, ) )
    
    mark_has_missing_information_target = get_submission_mark_has_missing_information( submission_id, "mark_target" )
    mark_has_missing_information_incidental = get_submission_mark_has_missing_information( submission_id, "mark_incidental" )
    nb_marks_target = get_submission_mark_information_details( submission_id )[ "mark_target" ][ "total" ]
    nb_marks_incidental = get_submission_mark_information_details( submission_id )[ "mark_incidental" ][ "total" ]
    has_missing_segmentations = get_submission_tenprint_has_missing_segmentations( submission_id )
    has_missing_gp = get_submission_has_missing_gp( submission_id )
    has_no_tp = get_submission_has_no_tenprint( submission_id )
    
    return utils.template.my_render_template(
        "submission/admin/submission_home.html",
        submission = submission,
        mark_has_missing_information_target = mark_has_missing_information_target,
        nb_marks_target = nb_marks_target,
        nb_marks_incidental = nb_marks_incidental,
        mark_has_missing_information_incidental = mark_has_missing_information_incidental,
        has_missing_segmentations = has_missing_segmentations,
        has_missing_gp = has_missing_gp,
        has_no_tp = has_no_tp
    )
    
@submission_view.route( "/admin/submission/list" )
@utils.decorator.admin_required
def admin_submission_list():
    """
        Get the list of all submissions folder.
    """
    current_app.logger.info( "Get all submissions" )
    
    sql = """
        SELECT submissions.id, submissions.uuid, users.username
        FROM submissions
        LEFT JOIN users ON submissions.donor_id = users.id
        ORDER BY created_time DESC
    """
    donors = config.db.query_fetchall( sql )
    
    current_app.logger.info( "{} submissions found".format( len( donors ) ) )
    
    return utils.template.my_render_template( 
        "submission/admin/submission_list.html",
        donors = donors
    )

@submission_view.route( "/admin/submission/table" )
@utils.decorator.admin_required
def admin_submission_table():
    """
        Get the list of all submissions with the counts related to each
        submission (number of marks, tenprintcards, ...).
    """
    sql = """
        SELECT
            submissions.id,
            submissions.uuid,
            users.username
        FROM submissions
        LEFT JOIN users ON submissions.donor_id = users.id
        ORDER BY created_time DESC
    """
    donors = config.db.query_fetchall( sql )
    
    sql = """
        SELECT
            submissions.uuid,
            files_type.name,
            count( files.uuid ) AS nb
        FROM files
        INNER JOIN submissions ON files.folder = submissions.id
        INNER JOIN files_type ON files.type = files_type.id
        GROUP BY submissions.uuid, files_type.name
    """
    counts = config.db.query_fetchall( sql )
    
    sql = """
        SELECT
            submissions.uuid,
            count( * ) AS nb
        FROM files_segments
        INNER JOIN files ON files_segments.tenprint = files.uuid
        INNER JOIN submissions ON files.folder = submissions.id
        GROUP BY submissions.uuid
    """
    segments = config.db.query_fetchall( sql )

    sql = """
        SELECT
            submissions.uuid,
            count( cnm_annotation.id ) AS nb
        FROM cnm_annotation
        LEFT JOIN cnm_folder ON cnm_annotation.folder_uuid = cnm_folder.uuid
        LEFT JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
        GROUP BY submissions.uuid
    """
    targets = config.db.query_fetchall( sql )
    
    current_app.logger.info( "{} submissions found".format( len( donors ) ) )
    
    return utils.template.my_render_template(
        "submission/admin/submission_table.html",
        donors = donors,
        counts = counts,
        segments = segments,
        targets = targets
    )
@submission_view.route( "/admin/<submission_id>/tenprint/list" )
@utils.decorator.admin_required
def admin_tenprint_list( submission_id ):
    """
        Get the list of all tenprints.
    """
    current_app.logger.info( "Get all tenprints cards" )
    
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
            ( files.type = 1 OR files.type = 2 OR files.type = 5 ) AND
            submissions.uuid = %s AND
            users.username IS NOT NULL
        ORDER BY users.id ASC, files.type, files.id ASC
    """
    data = ( submission_id, )
    
    tenprint_cards = config.db.query_fetchall( sql, data )
    
    sql = """
        SELECT users.username, submissions.uuid
        FROM submissions
        LEFT JOIN users ON submissions.donor_id = users.id
        WHERE submissions.uuid = %s
    """
    selector, submission_uuid = config.db.query_fetchone( sql, ( submission_id, ) )
        
    current_app.logger.info( "{} tenprints cards found".format( len( tenprint_cards ) ) )
    
    segments = get_submission_tenprint_segments_count( submission_id )
    
    return utils.template.my_render_template( 
        "submission/admin/tenprint_list.html",
        tenprint_cards = tenprint_cards,
        selector = selector,
        submission_uuid = submission_uuid,
        segments = segments
    )

@submission_view.route( "/admin/<submission_id>/tenprint/<tenprint_id>" )
@utils.decorator.admin_required
def admin_tenprint( submission_id, tenprint_id ):
    """
        Serve the page to see and edit a tenprint file.
    """
    current_app.logger.info( "Serve tenprint edit page for '{}', submission '{}'".format( tenprint_id, submission_id ) )
    sql = """
        SELECT
            files.uuid,
            files.format, files.resolution, files.width, files.height, files.size,
            files.creation_time, files.type,
            files.quality,
            users.username
        FROM files
        LEFT JOIN submissions ON files.folder = submissions.id
        LEFT JOIN users ON submissions.donor_id = users.id
        WHERE
            submissions.uuid = %s AND
            files.uuid = %s
    """
    tenprint_file = config.db.query_fetchone( sql, ( submission_id, tenprint_id, ) )
    
    current_app.logger.debug( "tenprint type: {}".format( tenprint_file[ "type" ] ) )
    
    if tenprint_file[ "type" ] == 5:
        current_app.logger.debug( "Redirect to the segments list page" )
        return redirect( url_for( "submission.tenprint_segments_list", submission_id = submission_id, tenprint_id = tenprint_id ) )
    
    else:
        tenprint_file[ "size" ] = round( 100 * float( tenprint_file[ "size" ] ) / ( 1024 * 1024 ) ) / 100
        
        if tenprint_file[ "type" ] == 1:
            side = "front"
        elif tenprint_file[ "type" ] == 2:
            side = "back"
        
        ############################################################################
        
        sql = "SELECT id, name FROM quality_type"
        quality_type = config.db.query_fetchall( sql )
        
        ############################################################################
        
        sql = "SELECT width, height, resolution FROM files WHERE uuid = %s LIMIT 1"
        img_info = config.db.query_fetchone( sql, ( tenprint_id, ) )
        svg_hw_factor = float( img_info[ "width" ] ) / float( img_info[ "height" ] )
        
        ############################################################################
        
        sql = "SELECT * FROM segments_locations WHERE tenprint_id = %s ORDER BY fpc ASC"
        zones_raw = config.db.query_fetchall( sql, ( tenprint_id, ) )
        zones = []
        
        for z in zones_raw:
            tmp = {}
            for k in [ "fpc", "orientation" ]:
                tmp[ k ] = z[ k ]
            
            for k in [ "x", "width" ]:
                tmp[ k ] = z[ k ] / img_info[ "width" ]
            for k in [ "y", "height" ]:
                tmp[ k ] = z[ k ] / img_info[ "height" ]
            
            zones.append( tmp )
        
        ############################################################################
        
        sql = "SELECT width, height, resolution FROM files WHERE uuid = %s LIMIT 1"
        img_info = config.db.query_fetchone( sql, ( tenprint_id, ) )
        svg_hw_factor = float( img_info[ "width" ] ) / float( img_info[ "height" ] )
        
        ############################################################################
        
        if side == "front":
            to_annotate = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ]
        else:
            to_annotate = [ 25, 27, 22, 24 ]
        
        ############################################################################
        
        return utils.template.my_render_template( 
            "submission/shared/tenprint.html",
            segments_position_code = segments_position_code,
            to_annotate = to_annotate,
            submission_id = submission_id,
            file = tenprint_file,
            img_info = img_info,
            svg_hw_factor = svg_hw_factor,
            zones = zones,
            quality_type = quality_type
        )

@submission_view.route( "/admin/submission/<submission_id>/tenprint/<tenprint_id>/segment/list" )
@utils.decorator.admin_required
def admin_submission_tenprint_segments_list( submission_id, tenprint_id ):
    """
        Serve the page with the list of segments for a tenprint image.
    """
    current_app.logger.info( "Get the list of segments for tenprint '{}', submission id '{}'".format( tenprint_id, submission_id ) )
    
    sql = """
        SELECT files_segments.pc, files_segments.data, pc.name
        FROM files_segments
        LEFT JOIN pc ON pc.id = files_segments.pc
        WHERE tenprint = %s
    """
    segments = config.db.query_fetchall( sql, ( tenprint_id, ) )
    nb_segments = len( segments )
    
    current_app.logger.debug( "{} segments stored in database".format( nb_segments ) )
    
    sql = """
        SELECT username
        FROM users
        LEFT JOIN submissions ON submissions.donor_id = users.id
        WHERE submissions.uuid = %s
    """
    donor_username = config.db.query_fetchone( sql, ( submission_id, ) )[ "username" ]
    
    ############################################################################
    
    return utils.template.my_render_template( 
        "submission/admin/segment_list.html",
        submission_id = submission_id,
        tenprint_id = tenprint_id,
        donor_username = donor_username,
        segments = segments,
        nb_segments = nb_segments
    )

@submission_view.route( "/admin/<submission_id>/gp" )
@utils.decorator.submission_has_access
def admin_submission_gp( submission_id ):
    """
        Serve the page to upload the general pattern for a donor.
    """
    current_app.logger.info( "Serve the page to set the GP for {}".format( submission_id ) )
    
    finger_names = []
    for laterality in [ "Right", "Left" ]:
        for finger in [ "thumb", "index", "middle", "ring", "little" ]:
            finger_names.append( "{} {}".format( laterality, finger ) )
    
    gp_list = [
        {
            "div_name": "ll",
            "name": "left loop"
        },
        {
            "div_name": "rl",
            "name": "right loop"
        },
        {
            "div_name": "whorl",
            "name": "whorl"
        },
        {
            "div_name": "arch",
            "name": "arch"
        },
        {
            "div_name": "cpl",
            "name": "central pocket loop"
        },
        {
            "div_name": "dl",
            "name": "double loop"
        },
        {
            "div_name": "ma",
            "name": "missing/amputated"
        },
        {
            "div_name": "sm",
            "name": "scarred/mutilated"
        },
        {
            "div_name": "unknown",
            "name": "unknown"
        }
    ]
    
    try:
        sql = """
            SELECT donor_fingers_gp.fpc, gp.div_name, gp.name
            FROM donor_fingers_gp
            LEFT JOIN submissions ON donor_fingers_gp.donor_id = submissions.donor_id
            LEFT JOIN gp ON donor_fingers_gp.gp = gp.id
            WHERE submissions.uuid = %s AND donor_fingers_gp.fpc <= 10
            ORDER BY donor_fingers_gp.fpc ASC
        """
        current_gp = config.db.query_fetchall( sql, ( submission_id, ) )
        
        utils.encryption.dek_check( submission_id )
        
        sql = """
            SELECT users.username
            FROM submissions
            LEFT JOIN users ON submissions.donor_id = users.id
            WHERE uuid = %s
        """
        donor = config.db.query_fetchone( sql, ( submission_id, ) )
        
        return utils.template.my_render_template( 
            "submission/admin/set_gp.html",
            submission_id = submission_id,
            finger_names = finger_names,
            gp_list = gp_list,
            current_gp = current_gp,
            donor = donor
        )
    
    except:
        return jsonify( {
            "error": True,
            "message": "Case not found"
        } )

@submission_view.route( "/submission/<submission_id>/mark/<mark_id>" )
@utils.decorator.submission_has_access
def submission_mark( submission_id, mark_id ):
    """
        Serve the page to edit a particular mark image. See the
        `submission_mark_inner` function for more details.
    """
    return submission_mark_inner( submission_id, mark_id, False )

@submission_view.route( "/admin/submission/<submission_id>/mark/<mark_id>" )
@utils.decorator.submission_has_access
def admin_submission_mark( submission_id, mark_id ):
    """
        Return the admin mark display mark. See the `submission_mark_inner` for
        more details.
    """
    return submission_mark_inner( submission_id, mark_id, True )

def submission_mark_inner( submission_id, mark_id, admin = False ):
    """
        Serve the page to edit a particular mark image.
    """
    current_app.logger.info( "Serve the mark page edit" )
    current_app.logger.debug( "submission {}".format( submission_id ) )
    current_app.logger.debug( "mark {}".format( mark_id ) )
    
    sql = """
        SELECT
            submissions.id,
            submissions.nickname,
            users.username
        FROM submissions
        INNER JOIN users ON submissions.donor_id = users.id
        WHERE uuid = %s
    """
    submission_folder_id, nickname, username = config.db.query_fetchone( sql, ( submission_id, ) )
    nickname = utils.encryption.do_decrypt_user_session( nickname )

    sql = """
        SELECT
            files.uuid, files.filename, files.note,
            files.format, files.resolution, files.width, files.height, files.size,
            files.creation_time, files.type,
            files_type.name as file_type
        
        FROM files
        LEFT JOIN files_type ON files.type = files_type.id
        WHERE
            folder = %s AND
            files.uuid = %s
    """
    
    mark = config.db.query_fetchone( sql, ( submission_folder_id, mark_id, ) )
    mark[ "size" ] = round( 100 * float( mark[ "size" ] ) / ( 1024 * 1024 ) ) / 100
    mark[ "filename" ] = utils.encryption.do_decrypt_user_session( mark[ "filename" ] )
    mark[ "file_type" ] = mark[ "file_type" ].replace( "mark_", "" )
    
    sql = "SELECT * FROM detection_technics ORDER BY name ASC"
    all_detection_tetchnics = config.db.query_fetchall( sql )
    
    sql = "SELECT * FROM surfaces ORDER BY name ASC"
    all_surfaces = config.db.query_fetchall( sql )
    
    sql = "SELECT * FROM activities ORDER BY name ASC"
    all_activities = config.db.query_fetchall( sql )

    sql = "SELECT * FROM distortion ORDER BY name ASC"
    all_distortions = config.db.query_fetchall( sql )

    try:
        sql = "SELECT detection_technic FROM mark_info WHERE uuid = %s"
        detection_technics = config.db.query_fetchone( sql, ( mark_id, ) )[ "detection_technic" ]
    except:
        detection_technics = ""
    
    try:
        sql = "SELECT surface FROM mark_info WHERE uuid = %s"
        surface = config.db.query_fetchone( sql, ( mark_id, ) )[ "surface" ]
    except:
        surface = ""
    
    try:
        sql = "SELECT activity FROM mark_info WHERE uuid = %s"
        activity = config.db.query_fetchone( sql, ( mark_id, ) )[ "activity" ]
    except:
        activity = ""
    
    try:
        sql = "SELECT distortion FROM mark_info WHERE uuid = %s"
        distortion = config.db.query_fetchone( sql, ( mark_id, ) )[ "distortion" ]
    except:
        distortion = ""
    
    try:
        sql = "SELECT pfsp FROM mark_info WHERE uuid = %s"
        current_pfsp = config.db.query_fetchone( sql, ( mark_id, ) )[ "pfsp" ]
    except:
        current_pfsp = ""
    
    return utils.template.my_render_template(
        "submission/shared/mark.html",
        submission_id = submission_id,
        nickname = nickname,
        file = mark,
        all_detection_technics = all_detection_tetchnics,
        all_surfaces = all_surfaces,
        all_activities = all_activities,
        all_distortions = all_distortions,
        detection_technics = detection_technics,
        surface = surface,
        activity = activity,
        distortion = distortion,
        current_pfsp = current_pfsp,
        pfsp_zones = pfsp.zones,
        username = username,
        admin = admin
    )

@submission_view.route( "/submission/<submission_uuid>/targets/download" )
@utils.decorator.login_required
def download_target_folder( submission_uuid ):
    sql = """
        SELECT
            cnm_annotation.uuid,
            cnm_folder.pc AS fpc
        FROM cnm_annotation
        LEFT JOIN cnm_folder ON cnm_annotation.folder_uuid = cnm_folder.uuid
        LEFT JOIN submissions ON cnm_folder.donor_id = submissions.donor_id
        WHERE
            submissions.uuid = %s
        ORDER BY cnm_folder.pc ASC
    """
    annotations = config.db.query_fetchall( sql, ( submission_uuid, ) )
    
    zipbuffer = StringIO()
    
    with zipfile.ZipFile( zipbuffer, "w", zipfile.ZIP_DEFLATED ) as fp:
        for fid in annotations:
            file_id, fpc = fid
            finger_name = segments_position_code[ fpc ]
            finger_name = finger_name.replace( " ", "_" )
            
            submission_id = views.images.get_submission_uuid_for_annotation( file_id )
            
            img, _ = views.images.image_serve( "cnm_annotation", file_id, submission_id )
            img = views.images.image_tatoo( img, file_id )
            
            buff = utils.images.pil2buffer( img, "TIFF" )
            fp.writestr(
                "finger_{}_{}_annotation_{}.tiff".format( fpc, finger_name, file_id ),
                buff.getvalue()
            )
            
    zipbuffer.seek( 0 )
    
    return send_file(
        zipbuffer,
        attachment_filename = "{}.zip".format( submission_uuid ),
        as_attachment = True
    )

