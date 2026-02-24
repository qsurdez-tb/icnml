#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from gevent import monkey
monkey.patch_all()

import logging
import os

from gevent.pywsgi import WSGIServer

from app import app

ICNML_SSL = os.environ.get( "ICNML_SSL", True )
ICNML_SSL = ICNML_SSL in [ "t", "T", True, "1" ]

certificatebase = os.environ.get( "CERTIFICATE_ROOT_PATH", "/tmp" )

KEY_FILE = "{}/key.pem".format( certificatebase )
CERT_FILE = "{}/cert.pem".format( certificatebase )

port = os.environ.get( "PORT", 5000 )

if ICNML_SSL and os.path.isfile( KEY_FILE ) and os.path.isfile( CERT_FILE ):
    http_server = WSGIServer( ( "0.0.0.0", port ), app, keyfile = KEY_FILE, certfile = CERT_FILE, log = logging.getLogger() )
else:
    http_server = WSGIServer( ( "0.0.0.0", port ), app, log = logging.getLogger() )

http_server.serve_forever()
