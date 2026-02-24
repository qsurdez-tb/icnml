#!/usr/bin/python
# -*- coding: UTF-8 -*-

import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

from cStringIO import StringIO
from PIL import Image

# Encryption

encryption_prefix = "icnml$"

def do_decrypt( data, password ):
    try:
        data = AESCipher( password ).decrypt( data )
        
        if data.startswith( encryption_prefix ):
            return data[ len( encryption_prefix ): ]
        else:
            return "-"
    
    except:
        return "-"

def do_encrypt( data, password ):
    return AESCipher( password ).encrypt( encryption_prefix + data )

class AESCipher( object ):
    def __init__( self, key ):
        self.key = hashlib.sha256( key.encode() ).digest()
    
    def encrypt( self, data ):
        data = self._pad( data )
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        
        iv = base64.b64encode( iv )
        encrypted = base64.b64encode( cipher.encrypt( data ) )
        
        return "$".join( map( str, [ "AES256", iv, encrypted ] ) )
    
    def decrypt( self, data ):
        _, iv, data = data.split( "$" )
        iv = base64.b64decode( iv )
        data = base64.b64decode( data )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return self._unpad( cipher.decrypt( data ) ).decode( "utf-8" )
    
    def _pad( self, s ):
        diff = AES.block_size - len( s ) % AES.block_size
        return s + diff * chr( diff )
    
    @staticmethod
    def _unpad( s ):
        return s[ :-ord( s[ len( s ) - 1: ] ) ]
    
# Image processing

def str2img( data ):
    if data == None:
        return None
    
    else:
        img = base64.b64decode( data )
        buff = StringIO()
        buff.write( img )
        buff.seek( 0 )
        img = Image.open( buff )
        
        return img
    
