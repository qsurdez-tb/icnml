#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import current_app, abort, send_file, jsonify, session

import base64
import barcode
import time
from cStringIO import StringIO
from threading import Lock
from uuid import uuid4

from PIL import Image
from PIL.TiffImagePlugin import TiffImageFile

import utils

from functions import no_preview_image

from NIST import NISTf

import config

lock = Lock()

image_view = Blueprint( "image", __name__, template_folder = "template" )

@utils.redis.redis_cache( 300 )
def get_submission_uuid_for_file( file_uuid ):
    """
        Get the related submission uuid for a file uuid.
    """
    sql = """
        SELECT submissions.uuid
        FROM submissions
        LEFT JOIN files ON submissions.id = files.folder
        WHERE files.uuid = %s
    """
    return config.db.query_fetchone( sql, ( file_uuid, ) )[ "uuid" ]

def get_submission_uuid_for_annotation( file_uuid ):
    sql = """
        SELECT submissions.uuid
        FROM submissions
        LEFT JOIN cnm_folder ON submissions.donor_id = cnm_folder.donor_id
        LEFT JOIN cnm_annotation ON cnm_annotation.folder_uuid = cnm_folder.uuid
        WHERE cnm_annotation.uuid = %s
    """
    return config.db.query_fetchone( sql, ( file_uuid,  ) )[ "uuid" ]

@image_view.route( "/image/file/<file_id>/preview" )
@image_view.route( "/image/file/preview" )
@utils.decorator.login_required
def image_file_serve( file_id = None ):
    img = image_file_serve_inner( file_id )
    
    if isinstance( img, TiffImageFile ):
        if not hasattr( img, "use_load_libtiff" ):
            img.use_load_libtiff = True
    
    if img == None:
        return abort( 404 )
    
    else:
        buff = utils.images.pil2buffer( img, "JPEG" )
        return send_file( buff, mimetype = "image/jpeg" )
    
@image_view.route( "/image/file/<file_id>/tiff" )
@utils.decorator.login_required
def image_file_serve_raw( file_id = None ):
    img = image_file_serve_inner( file_id, True )
    
    if isinstance( img, TiffImageFile ):
        if not hasattr( img, "use_load_libtiff" ):
            img.use_load_libtiff = True
    
    # Image resampling to 1000dpi
    res, _ = img.info[ 'dpi' ]
    
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
        attachment_filename = "{}.tiff".format( file_id, )
    )

def image_file_serve_inner( file_id, raw = False ):
    """
        Function to get an image from the database and return it as PNG preview image.
    """
    current_app.logger.info( "Serve a preview for the file '{}'".format( file_id ) )
    
    try:
        if file_id == None:
            raise Exception( "No file id" )
        
        submission_id = get_submission_uuid_for_file( file_id )
        current_app.logger.debug( "submission id: '{}'".format( submission_id ) )
        
        if raw:
            img, _ = image_serve( "files", file_id, submission_id )
            return img
        
        else:
            img, _ = image_serve( "thumbnails", file_id, submission_id )
            
            if img == None:
                current_app.logger.debug( "No image in the 'thumnnails' database. Recreating the thumbnail" )
                
                img, _ = image_serve( "files", file_id, submission_id )
                
                if img == None:
                    return None
                
                if not raw:
                    current_app.logger.debug( "Image from the 'files' table: {}".format( img ) )
                    img = utils.images.create_thumbnail( file_id, img, submission_id )
                    current_app.logger.debug( "Thumbnail image: {}".format( img ) )
            
            return img
    
    except:
        current_app.logger.error( "Error while creating the thumbnail. Serving a 'no preview' image" )
        return no_preview_image( return_pil = True )

@image_view.route( "/image/file/<file_id>/full_resolution" )
@utils.decorator.admin_required
def admin_download_file_full_resolution( file_id ):
    """
        Download the full resolution of an image. This function is only
        accessible for admins. The downloaded image will not be tagged like the
        other images.
    """
    try:
        if file_id == None:
            raise Exception( "No file id" )
        
        submission_id = get_submission_uuid_for_file( file_id )
        current_app.logger.debug( "submission id: '{}'".format( submission_id ) )
        
        img, _ = image_serve( "files", file_id, submission_id )
        
        if img == None:
            return abort( 404 )
            
        buff = utils.images.pil2buffer( img, "TIFF" )
        return send_file(
            buff,
            mimetype = "image/tiff",
            as_attachment = True,
            attachment_filename = file_id + ".tiff",
        )
    
    except:
        return abort( 403 )
        
@image_view.route( "/image/segment/<tenprint_id>/<pc>" )
@utils.decorator.login_required
def image_segment_serve( tenprint_id, pc ):
    """
        Serve a preview for a segment image.
    """
    current_app.logger.info( "Serving a segment image for the tenprint '{}', pc '{}'".format( tenprint_id, pc ) )
    
    try:
        submission_id = get_submission_uuid_for_file( tenprint_id )
        
        current_app.logger.debug( "submission id: {}".format( submission_id ) )
        
        img, _ = image_serve( "files_segments", ( tenprint_id, pc ), submission_id )
        img = utils.images.create_thumbnail( None, img, submission_id )
        
        current_app.logger.debug( "image: {}".format( img ) )
        
        buff = utils.images.pil2buffer( img, "JPEG" )
        return send_file( buff, mimetype = "image/jpeg" )
    
    except:
        current_app.logger.error( "Error while creating the thumbnail. Serving a 'no preview' image" )
        return send_file( no_preview_image(), mimetype = "image/png" )

@image_view.route( "/image/annotation/<uuid>" )
@utils.decorator.login_required
def image_annotation_serve( uuid ):
    submission_id = get_submission_uuid_for_annotation( uuid )
    
    img, _ = image_serve( "cnm_annotation", uuid, submission_id )
    img = utils.images.create_thumbnail( None, img, submission_id )
    
    buff = utils.images.pil2buffer( img, "JPEG" )
    return send_file( buff, mimetype = "image/jpeg" )
    
def image_serve( table, image_id, submission_id ):
    """
        Backend function to get the image from the database.
    """
    current_app.logger.info( "Serve the image '{}' for submission '{}' from table '{}'".format( image_id, submission_id, table ) )
    
    need_to_decrypt_with_donor_dek = True
    
    if table == "files_segments":
        sql = """
            SELECT
                files_segments.data,
                files_segments.uuid,
                files.resolution
            FROM {}
            LEFT JOIN files ON files.uuid = files_segments.tenprint
            WHERE
                files_segments.tenprint = %s
        """.format( table )
        
        if isinstance( image_id, tuple ):
            tp, pc = image_id
            sql += " AND files_segments.pc = %s"
            p = ( tp, pc, )
        else:
            sql += " AND files_segments.uuid = %s"
            p = ( image_id, )
    
    elif table == "files":
        sql = "SELECT data, uuid, resolution, format FROM {} WHERE uuid = %s".format( table )
        p = ( image_id, )
    
    elif table == "thumbnails":
        sql = "SELECT data, uuid, format FROM {} WHERE uuid = %s".format( table )
        p = ( image_id, )
    
    elif table == "cnm_annotation":
        sql = "SELECT data, uuid FROM {} WHERE uuid = %s".format( table )
        p = ( image_id, )
        
    elif table == "cnm_candidate":
        sql = "SELECT data, uuid FROM cnm_candidate WHERE uuid = %s"
        p = ( image_id, )
        need_to_decrypt_with_donor_dek = False
        
    else:
        current_app.logger.error( "table '{}' not authorized".format( table ) )
        raise Exception( "table not authorized" )
    
    current_app.logger.debug( "sql:    {}".format( sql ) )
    current_app.logger.debug( "params: {}".format( p ) )
    
    data = config.db.query_fetchone( sql, p )
    
    if data == None:
        return None, None
    
    else:
        img = data[ "data" ]
        rid = data[ "uuid" ]
        
        if img == None:
            return None, None
        
        current_app.logger.debug( "image: {}...".format( img[ 0:20 ] ) )
        current_app.logger.debug( "need_to_decrypt_with_donor_dek: {}".format( need_to_decrypt_with_donor_dek ) )
        if "format" in data:
            current_app.logger.debug( "format: {}".format( data[ "format" ] ) )
        
        if need_to_decrypt_with_donor_dek:
            img = utils.encryption.do_decrypt_dek( img, submission_id )
        
        if table == "files" and data[ "format" ].upper() == "NIST":
            img = str2nist2img( img )
        else:
            img = str2img( img )
        
        img = utils.images.patch_image_to_web_standard( img )
            
        if "resolution" in data:
            img.info[ "dpi" ] = ( data[ "resolution" ], data[ "resolution" ] )

        current_app.logger.debug( "image: {}".format( img ) )
        
        return img, rid

def str2img( data ):
    """
        Convert a base64 string image to a PIL image.
    """
    current_app.logger.info( "Convert string image to PIL format" )
    
    if data == None:
        return None
    
    else:
        img = base64.b64decode( data )
        buff = StringIO()
        buff.write( img )
        buff.seek( 0 )
        img = Image.open( buff )
        
        current_app.logger.debug( "string: {}".format( data[ 0:20 ] ) )
        current_app.logger.debug( "image: {}".format( img ) )
        
        return img

def str2nist2img( data ):
    """
        Convert a NIST string object to the tenprint card image.
    """
    current_app.logger.info( "Convert string NIST file to tenprint card image" )
    
    if data == None:
        return None
    
    else:
        img = base64.b64decode( data )
        buff = StringIO()
        buff.write( img )
        buff.seek( 0 )
        
        with lock:
            n = NISTf( buff )
            img = n.get_tenprintcard_front( 1000 )
        
        current_app.logger.debug( "string: {}".format( data[ 0:20 ] ) )
        current_app.logger.debug( "image: {}".format( img ) )
        
        return img

def tag_bottom( img, data ):
    """
        Add fingerprinting to the image at the bottom. This will add the
        argument `data` to the images as a CODE128 barcode at the top of the
        image.
    """
    data = str( data )

    top = 10
    h = 10
    
    fp = StringIO()
    options = {
        'module_width': 0.2,
        'module_height': 1.0,
        'quiet_zone': 0,
        'write_text': False,
    }
    barcode.generate( 'code128', data, writer = barcode.writer.ImageWriter(), output = fp, writer_options = options )
    codebar_img = Image.open( fp )
    codebar_img = codebar_img.crop( ( 0, top, codebar_img.width, top + h ) )
    
    size = list( img.size )
    size[ 1 ] += h

    if img.mode == "RGB":
        bg = ( 255, 255, 255 )
    else:
        bg = 255

    ret = Image.new( img.mode, size, bg )
    ret.paste( img, ( 0, 0 ) )
    ret.paste( codebar_img, ( size[ 0 ] - codebar_img.size[ 0 ], size[ 1 ] - codebar_img.size[ 1 ] ) )

    return ret

def tag_visible( img, data ):
    """
        Add fingerprinting to the image at the bottom. This will add the
        argument `data` to the images as a CODE128 barcode at the bottom of the
        image.
    """
    data = str( data )

    fp = StringIO()
    options = {
        'module_width': 0.2,
        'module_height': 4,
        'quiet_zone': 2,
        'font_size': 10,
        'text_distance': 1,
    }
    barcode.generate( 'code128', data, writer = barcode.writer.ImageWriter(), output = fp, writer_options = options )
    codebar_img = Image.open( fp )
    
    size = list( img.size )
    size[ 1 ] += codebar_img.size[ 1 ]

    if img.mode == "L":
        bg = 255
        mode = "L"
    else:
        bg = ( 255, 255, 255 )
        mode = "RGB"

    ret = Image.new( mode, size, bg )
    ret.paste( img, ( 0, codebar_img.size[ 1 ] ) )
    ret.paste( codebar_img, ( size[ 0 ] - codebar_img.size[ 0 ], 0 ) )

    return ret

def image_tatoo( img, image_id ):
    """
        Add the user and download information on the provided image. This
        information is generated automatically for every download of an image.
    """
    image_id = image_id[ 0:18 ]
    res = img.info.get( "dpi", ( 72, 72 ) )
    
    img = tag_visible( img, image_id )
    img = tag_bottom( img, "{} {}".format( session[ "user_id" ], time.time() ) )
    
    img.info[ "dpi" ] = res
    
    return img

@image_view.route( "/image/file/<image_id>/info" )
@utils.decorator.login_required
def img_info( image_id ):
    """
        Get and return the metadata for a particular image. See do_img_info()
        for more informations.
    """
    current_app.logger.info( "Serve image informations for image '{}'".format( image_id ) )
    
    d = do_img_info( image_id )
    
    if d != None:
        return jsonify( d )
    else:
        return abort( 404 )

@utils.redis.redis_cache( 300 )
def do_img_info( image_id ):
    """
        Retrieve the metadata for a particular image from the database.
    """
    current_app.logger.debug( "Get image information from database for '{}'".format( image_id ) )
    
    sql = """
        SELECT
            size, width, height, resolution, format
        FROM files
        WHERE uuid = %s
    """
    d = config.db.query_fetchone( sql, ( image_id, ) )
    
    for key, value in d.iteritems():
        current_app.logger.debug( "{}: {}".format( key, value ) )
    
    if d != None:
        return dict( d )
    else:
        return None

@image_view.route( "/image/segment/<tenprint_id>/start" )
@utils.decorator.login_required
def image_tenprint_segmentation( tenprint_id ):
    """
        Route to start the segmentation of a tenprint image into segments
        (fingers or palm images).
    """
    current_app.logger.info( "Start segmentations for '{}'".format( tenprint_id ) )
    
    ret = do_image_tenprint_segmentation( tenprint_id )
    
    return jsonify( {
        "error": False,
        "data": ret
    } )

def do_image_tenprint_segmentation( tenprint_id ):
    """
        Backend function to create all the segments images for a tenprint souce image.
    """
    sql = "SELECT size, resolution, type, format, data FROM files WHERE uuid = %s"
    img = config.db.query_fetchone( sql, ( tenprint_id, ) )
    
    for key, value in img.iteritems():
        if isinstance( value, str ) and len( value ) > 20:
            value = "{}...".format( value[ 0:20 ] )
        current_app.logger.debug( "{}: {}".format( key, value ) )
    
    img_format = img[ "format" ]
    side = {
        1: "front",
        2: "back"
    }[ img[ "type" ] ]
    
    current_app.logger.debug( "side: {}".format( side ) )
    
    submission_id = get_submission_uuid_for_file( tenprint_id )
    
    current_app.logger.debug( "Decrypt data with DEK" )
    img = utils.encryption.do_decrypt_dek( img[ "data" ], submission_id )
    img = base64.b64decode( img )
    
    buff = StringIO()
    buff.write( img )
    buff.seek( 0 )
    img = Image.open( buff )
    
    current_app.logger.debug( "image: {}".format( img ) )
    
    sql = "SELECT * FROM segments_locations WHERE tenprint_id = %s"
    data = ( tenprint_id, )
    zones = config.db.query_fetchall( sql, data )
    
    sql = "DELETE FROM files_segments WHERE tenprint = %s"
    config.db.query( sql, ( tenprint_id, ) )
    
    for z in zones:
        current_app.logger.debug( "Segmenting fpc '{}'".format( z[ "fpc" ] ) )
        
        tl_x, tl_y, br_x, br_y = [ z[ "x" ], z[ "y" ], z[ "x" ] + z[ "width" ], z[ "y" ] + z[ "height" ] ]
        tmp = img.crop( ( tl_x, tl_y, br_x, br_y ) )
        
        if z[ "orientation" ] != 0:
            tmp = tmp.rotate( -z[ "orientation" ], Image.BICUBIC, True )
        
        buff = StringIO()
        tmp.save( buff, format = img_format )
        buff.seek( 0 )
        
        current_app.logger.debug( "Encrypting segment image with DEK" )
        file_data = buff.getvalue()
        file_data = base64.b64encode( file_data )
        file_data = utils.encryption.do_encrypt_dek( file_data, submission_id )
        
        current_app.logger.debug( "Inserting to the database" )
        sql = utils.sql.sql_insert_generate( "files_segments", [ "tenprint", "uuid", "pc", "data" ] )
        data = ( tenprint_id, str( uuid4() ), z[ "fpc" ], file_data )
        config.db.query( sql, data )
        
    
    return True

@image_view.route( "/image/no_preview" )
def get_no_preview_image():
    return send_file( no_preview_image(), mimetype = "image/png" )

