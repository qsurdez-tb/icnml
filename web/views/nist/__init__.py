#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
import cStringIO

from flask import Blueprint
from flask import jsonify, send_file, current_app

import utils
import config

from NIST.fingerprint import NISTf_auto

nist_view = Blueprint( "nist", __name__, template_folder = "templates" )

def cnm_candidate_get_image( cnm_uuid, file_uuid, fpc ):
    sql = """
        SELECT data
        FROM cnm_candidate
        WHERE
            cnm_result = %s AND
            uuid = %s
    """
    data = config.db.query_fetchone( sql, ( cnm_uuid, file_uuid, ) )[ "data" ]
    
    img = data2img( data, fpc )
    return img

def data2img( data, fpc ):
    data = data2nist( data )
    return nist2img( data, fpc )

def data2nist( data ):
    data = base64.decodestring( data )
    buffer = cStringIO.StringIO()
    buffer.write( data )
    
    n = NISTf_auto( buffer )
    
    return n
    
def nist2img( n, fpc ):
    fpc = int( fpc )
    if fpc == 0:
        fpc = n.get_fpc_list()[ 0 ]
    
    return n.get_image( fpc = fpc )

def nist_get_image_resolution( cnm_uuid, file_uuid, fpc ):
    sql = """
        SELECT data
        FROM cnm_candidate
        WHERE
            cnm_result = %s AND
            uuid = %s
    """
    data = config.db.query_fetchone( sql, ( cnm_uuid, file_uuid, ) )[ "data" ]
    
    n = data2nist( data )
    ntype, idc = n.search_fpc( fpc )
    res = n.get_resolution( idc )
    height = n.get_height( idc )
    width = n.get_width( idc )
    
    return (res, width, height)

