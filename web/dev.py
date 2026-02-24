#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from app import app

debug = os.environ.get( "DEBUG", False ) in [ "True", "true", "1" ]

KEY_FILE = "./key.pem"
CERT_FILE = "./cert.pem"

port = os.environ.get( "PORT", 5000 )

if __name__ == "__main__":
    if os.path.isfile( CERT_FILE ) and os.path.isfile( KEY_FILE ):
        app.run( debug = debug, host = "0.0.0.0", port = port, threaded = True, ssl_context = ( CERT_FILE, KEY_FILE ) )
    else:
        app.run( debug = debug, host = "0.0.0.0", port = port, threaded = True )
