#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from MDmisc.database import Database
from PiAnoS import Database as DatabasePiAnoS
import os

from PIL import Image
import gnupg
import redis
import random
import string
import utils.hash

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

baseurl = os.environ.get( "BASEURL", "" )
envtype = os.environ.get( "ENVTYPE", "" )

def random_data( N ):
    return "".join( random.choice( string.ascii_uppercase + string.digits ) for _ in range( N ) )

SECRET_KEY = os.environ.get( "SECRET_KEY", random_data( 20 ) )

MAX_CONTENT_LENGTH = 500 * 1024 * 1024

EMAIL_NB_ITERATIONS = 50 * 1000
PASSWORD_NB_ITERATIONS = 50 * 1000
DEK_NB_ITERATIONS = 500 * 1000
CF_NB_ITERATIONS = 100 * 1000

EMAIL_SALT_LENGTH = 20
PASSWORD_SALT_LENGTH = 20
DEK_SALT_LENGTH = 20
DEK_CHECK_SALT_LENGTH = 20

SESSION_TYPE = "redis"
SESSION_PERMANENT = False
SESSION_REFRESH_EACH_REQUEST = True

PERMANENT_SESSION_LIFETIME = 2 * 60 * 60

fake_hash = utils.hash.pbkdf2( word = "fake_data", salt = "fake_salt", iterations = 20000, hash_name = "sha512" ).hash()
fake_hash_stored = utils.hash.pbkdf2( fake_hash, "A" * PASSWORD_SALT_LENGTH, PASSWORD_NB_ITERATIONS ).hash()

TOTP_VALIDWINDOW = 5
TOTP_MAX_VALIDWINDOW = 1000

PROXY = os.environ.get( "BEHIND_PROXY", True )

login_rate_limiting_base = os.environ.get( "LOGIN_RATE_LIMITING_BASE", 2 )
login_rate_limiting_limit = os.environ.get( "LOGIN_RATE_LIMITING_LIMIT", 5 )

if "DB_PIANOS_URL" in os.environ:
    pianosurl = os.environ[ "DB_PIANOS_URL" ]
    pianosdb = DatabasePiAnoS( pianosurl )
    pianosendpoint = os.environ.get( "PIANOS_ENDPOINT", "/pianos" )
else:
    pianosdb = None
    pianosendpoint = None

if "DB_URL" in os.environ:
    dburl = os.environ[ "DB_URL" ]
    db = Database( dburl )
    # Set the database to be in auto-commit mode.
    # DO NOT CHANGE THE MODE TO TRANSACTION MODE (THE DEFAULT ONE) WITHOUT
    # CHANGING THE PING() FUNCTION!!! THE ENTIRE APPLICATION WILL NOT WORK
    # BECAUSE OF THE PING() HEALTHCHECK! READ MORE ABOUT THIS IN THE GIT COMMIT
    # MESSAGE.
    db.conn.set_isolation_level( ISOLATION_LEVEL_AUTOCOMMIT )
    # DO NOT CHANGE ONLY THIS
else:
    db = None

if "REDIS_URL" in os.environ:
    base_redis_url = os.environ.get( "REDIS_URL", "redis://redis:6379" )
    redis_dbs = {}
    for index, key in enumerate( [ "sessions", "cache", "totp", "reset", "rate_limit" ] ):
        try:
            url = os.environ.get( "REDIS_URL_{}".format( key.upper() ), "{}/{}".format( base_redis_url, index ) )
            redis_dbs[ key ] = redis.from_url( url )
            
        except:
            redis_dbs[ key ] = None
    
    SESSION_REDIS = redis_dbs[ "sessions" ]
else:
    redis_dbs = None
    SESSION_REDIS = None

smtpserver = os.environ.get( "SMTP_SERVER", "smtpauth.unil.ch" )
smtpport = os.environ.get( "SMTP_PORT", 587 )
smtpuser = os.environ.get( "SMTP_USERNAME", "username" )
smtppassword = os.environ.get( "SMTP_PASSWORD", "password" )
sender = os.environ.get( "SMTP_SENDER", "icnml@unil.ch" )

POPPLER_PATH = os.environ.get( "POPPLER_PATH", "" )

if envtype.upper() != "DEV":
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Strict"
    domain = "https://icnml.unil.ch"
    RP_ID = "icnml.unil.ch"

else:
    domain = os.environ.get( "DOMAIN", "http://localhost" )
    RP_ID = os.environ.get( "RPID", "localhost" )

baseurl = os.environ.get( "BASEURL", "" )
fulldomain = domain + baseurl
cdn = fulldomain + "/cdn"

ORIGIN = domain
rp_name = "ICNML"

gpg_key = ( "FB15B70D1507B18B", )
keys_folder = os.environ.get( "KEYS_FOLDER", "/keys" )
gnupg._parsers.Verify.TRUST_LEVELS[ "ENCRYPTION_COMPLIANCE_MODE" ] = 23

Image.MAX_IMAGE_PIXELS = 1 * 1024 * 1024 * 1024

NIST_file_extensions = [
    ".nist", ".nst",
    ".an2", ".an2k",
    ".xml",
    ".lffs", ".lff",
    ".lfis", ".lfi",
    ".irq", ".irr", ".isr",
    ".srl",
    ".lsmq", ".lsmr",
    ".lpnq", ".lpn", ".lpnr",
    ".ulac", ".uld",
    ".ular", ".uldr", ".uuld",
    ".errl", ".erri", ".erra", ".err"
]

all_fpc = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 25, 27, 22, 24 ]
finger_fpc = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ]
palm_fpc = [ 25, 27, 22, 24 ]

cdnfiles = [
    "jquery/js/jquery-3.6.0.min.js",
    "jquery/js/jquery-ui-1.12.1.min.js",
    "jquery/js/jquery.svg.js",
    "toastr/toastr.min.js",
    "misc/md5-min.js",
    "sha512.js",
    "moment.min.js",
    "base64.js",
    "otplib-browser.js",
    "dropzone/dropzone.js",
    "crypto-js/rollups/aes.js",
    "crypto-js/rollups/pbkdf2.js",
    "underscore-min.js",
    "chosen/chosen.js",
    "rangeslider/rangeslider.min.js",
    "jquery/css/base/jquery-ui.min.css",
    "jquery/css/jquery.svg.css",
    "toastr/toastr.min.css",
    "dropzone/dropzone.css",
    "loadingcss/loading-btn.css",
    "loadingcss/loading.css",
    "chosen/chosen.css",
    "rangeslider/rangeslider.min.css"
]

try:
    appfiles = os.listdir( "./app" )
except:
    appfiles = []

misc = {
    "jquery_ui_white_bg_icons": "/cdn/jquery/css/base/images/ui-icons_ffffff_256x240.png"
}

gpg_options = {
    "binary": os.environ.get( "GPG_BIN", "gpg" ),
    "homedir": os.environ.get( "GPG_HOMEDIR", "/tmp/gpg" )
}

gpg = gnupg.GPG( **gpg_options )

try:
    for key_file in os.listdir( keys_folder ):
        with open( keys_folder + "/" + key_file, "r" ) as fp:
            gpg.import_keys( fp.read() )
except:
    pass


account_type_id_name = {}
try:
    sql = "SELECT id, name FROM account_type"
    for at in db.query_fetchall( sql ):
        account_type_id_name[ at[ "id" ] ] = at[ "name" ]
except:
    pass

