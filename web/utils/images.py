#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
from cStringIO import StringIO

from PIL import ExifTags, Image
from flask import current_app

import numpy as np

import config
from . import encryption
from . import sql

def rotate_image_upon_exif( img ):
    """
        Rotate a `PIL.Image` based upon the EXIF information present in the `PIL` object.

        :param img: Image to rotate
        :type img: `PIL.Image`
        
        :return: Rotated image
        :rtype: `PIL.Image`
    """
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[ orientation ] == "Orientation":
                break
        
        exif = dict( img._getexif().items() )
    
        if exif[orientation] == 3:
            img = img.rotate( 180, expand = True )
        
        elif exif[orientation] == 6:
            img = img.rotate( 270, expand = True )
        
        elif exif[orientation] == 8:
            img = img.rotate( 90, expand = True )
    
    except ( AttributeError, KeyError, IndexError ):
        pass
    
    return img

def pil2buffer( img, img_format ):
    """
        Convert a image object to a python file-like object.
        This function is used to facilitate the use of `PIL.Image` python objects by acting like files.
        
        :param img: Input image
        :type img: `PIL.Image`

        :param img_format: Format to convert the image to
        :type img_format: str
        
        :return: Python file-like object
        :rtype: `cStringIO.StringIO`
    """
    buff = StringIO()
    
    if img.mode in [ "P", "PA" ]:
        img = img.convert( "RGB" )
    
    res = img.info.get( "dpi", ( 72, 72 ) )
    
    img.save( buff, format = img_format, dpi = res )
    buff.seek( 0 )
    
    return buff

def create_thumbnail( file_uuid, img, submission_id ):
    """
        Generate a thumbnail image for a PIL image passed in argument.
        
        :param file_uuid: UUID of the file to create a thumbnails for
        :type file_uuid: str

        :param img: Image to make a thumbnails for
        :type img: `PIL.Image`

        :param submission_id: Submission UUID related to the image
        :type submission_id: str
        
        :return: Thumbnail image
        :rtype: `PIL.Image`
    """
    current_app.logger.info( "Creating a thumbnail for the file '{}', submission '{}'".format( file_uuid, submission_id ) )
    current_app.logger.debug( "Input image: {}".format( img ) )
    
    img.thumbnail( ( 1000, 1000 ) )
    width, height = img.size
    
    current_app.logger.debug( "Thumbnail: {}".format( img ) )
    
    img_format = img.format
    buff = StringIO()
    
    if img_format == None:
        img.save( buff, format = "png" )
        img_format = "png"
    elif img_format.upper() in [ "TIFF", "TIF" ]:
        img.save( buff, format = img_format, compression = "raw" )
    else:
        img.save( buff, format = img_format )
    
    img_size = buff.tell()
    buff.seek( 0 )
    
    if file_uuid != None:
        current_app.logger.debug( "Encrypt the thumnbnail with DEK" )
        img_data = buff.getvalue()
        img_data = base64.b64encode( img_data )
        img_data = encryption.do_encrypt_dek( img_data, submission_id )
        
        current_app.logger.debug( "Saving thumnbail to database" )
        sql_query = sql.sql_insert_generate( "thumbnails", [ "uuid", "width", "height", "size", "format", "data" ] )
        data = ( file_uuid, width, height, img_size, img_format, img_data, )
        config.db.query( sql_query, data )
    
    return img

def patch_image_to_web_standard( img ):
    if img.mode == "I;16":
        img = np.asarray( img )
        img = img / float( np.power( 2, 16 ) ) * 255
        img = Image.fromarray( np.uint8( img ) )
        img.format = "TIFF"
    
    elif img.mode == "RGBA":
        img = img.convert( "RGB" )
    
    return img

