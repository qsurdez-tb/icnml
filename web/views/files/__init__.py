#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import send_from_directory

import config

files_view = Blueprint( "files", __name__ )

@files_view.route( "/cdn/<path:subpath>" )
def send_cdn_files( subpath ):
    """
        Serve the files from the cdn directory.
    """
    return send_from_directory( "cdn", subpath )

@files_view.route( "/app/<path:subpath>" )
def send_app_files( subpath ):
    """
        Serve the file from the app directory (all files related to the ICNML application).
    """
    return send_from_directory( "app", subpath )

@files_view.route( "/static/<path:subpath>" )
def send_static_files( subpath ):
    """
        Serve static files from the static directory.
    """
    return send_from_directory( "static", subpath )
