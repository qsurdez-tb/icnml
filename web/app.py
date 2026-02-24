#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from logging.config import dictConfig
import logging

from flask import Flask
from flask import request, has_request_context
from flask import session
from flask_compress import Compress
from flask_session import Session
from werkzeug.http import http_date
from werkzeug.middleware.proxy_fix import ProxyFix
import re

import config

################################################################################

logrequestre = re.compile( r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*\[[^\]]+\]\s(.*)" )

class RequestFormatter( logging.Formatter ):
    def format( self, record ):
        if has_request_context():
            try:
                username = session[ "username" ] 
            except:
                username = "-"
            
            record.msg = "{REMOTE_ADDR} (" + username + ") - " + record.msg
            record.msg = record.msg.format( **request.headers.environ )
        
        m = logrequestre.match( record.msg )
        if m:
            record.msg = m.group( 2 )
        
        return super( RequestFormatter, self ).format( record )

class myFilter( object ):
    def filter( self, record ):
        if "{}/ping".format( config.baseurl ) in record.msg and " 200 " in record.msg:
            return 0
        else:
            return 1

class myStreamHandler( logging.StreamHandler ):
    def __init__( self ):
        logging.StreamHandler.__init__( self )
        self.addFilter( myFilter() )

dictConfig( {
    "version": 1,
    "formatters": {
        "default": {
            "()": "app.RequestFormatter",
            "format": "[%(asctime)s] %(levelname)s: \t%(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "app.myStreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [ "console" ]
    }
} )

################################################################################

app = Flask( __name__ )
app.config.from_pyfile( "config.py" )

Compress( app )
Session( app )

if config.PROXY:
    app.wsgi_app = ProxyFix( app.wsgi_app )

################################################################################
#    Import the views

from views.base import base_view
app.register_blueprint( base_view, url_prefix = config.baseurl )

from views.adm import adm_view
app.register_blueprint( adm_view, url_prefix = config.baseurl )
app.register_blueprint( adm_view, url_prefix = "/" )

from views.files import files_view
app.register_blueprint( files_view, url_prefix = config.baseurl )

from views.login import login_view
app.register_blueprint( login_view, url_prefix = config.baseurl )

from views.newuser import newuser_view
app.register_blueprint( newuser_view, url_prefix = config.baseurl )

from views.donor import donor_view
app.register_blueprint( donor_view, url_prefix = config.baseurl )

from views.submission import submission_view
app.register_blueprint( submission_view, url_prefix = config.baseurl )

from views.images import image_view
app.register_blueprint( image_view, url_prefix = config.baseurl )

from views.nist import nist_view
app.register_blueprint( nist_view, url_prefix = config.baseurl )

from views.pianos import pianos_view
app.register_blueprint( pianos_view, url_prefix = config.baseurl )

from views.afis import afis_view
app.register_blueprint( afis_view, url_prefix = config.baseurl )

from views.trainer import trainer_view
app.register_blueprint( trainer_view, url_prefix = config.baseurl )

from views.uuid import uuid_view
app.register_blueprint( uuid_view, url_prefix = config.baseurl )

from views.shared import shared_view
app.register_blueprint( shared_view, url_prefix = config.baseurl )

