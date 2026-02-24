#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

encryption_prefix = "icnml$"

def do_decrypt( data, password ):
    """
        Decrypt the data passed in parameter (`data`) with the configured decryption function.
        This function is only here to facilitate the use of the decryption process in the application.
        If the encryption function shall be changed to an other one, do it here.
        
        :param data: Data to decrypt
        :type data: str

        :param password: Decryption key
        :type password: str

        :return: Decrypted data
        :rtype: str
    """
    try:
        data = AESCipher( password ).decrypt( data )
        
        if data.startswith( encryption_prefix ):
            return data[ len( encryption_prefix ): ]
        else:
            return "-"
    
    except:
        return "-"

def do_encrypt( data, password ):
    """
        Encrypt the data passed in parameter (`data`) with the configured decryption function.
        This function is only here to facilitate the use of the encryption process in the application.
        If the encryption function shall be changed to an other one, do it here.
        
        :param data: Data to encrypt
        :type data: str

        :param password: Encryption key
        :type password: str

        :return: Encrypted data
        :rtype: str
    """
    return AESCipher( password ).encrypt( encryption_prefix + data )

class AESCipher( object ):
    """
        Wrapper class around the `Crypto.Cipher.AES` function.
        This class is only here to facilitate the set of the default parameters for the `Crypto.Cipher.AES` function.
        
        Parameters used by default:

            - Hash (sha256) of the input password used as encryption key.
            - Random value for the Initialization Vector (size of the AES block)
            - AES CBC mode
            - padded input (mandatory).
    """
    def __init__( self, key ):
        self.key = hashlib.sha256( key.encode() ).digest()
    
    def encrypt( self, data ):
        """
            Encrypt the data passed in parameter with AES.
            The encrypted data will contain the encryption parameters.

            :param data: Data to encrypt
            :type data: str

            :return: Encrypted data
            :rtype: str
        """
        data = self._pad( data )
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        
        iv = base64.b64encode( iv )
        encrypted = base64.b64encode( cipher.encrypt( data ) )
        
        return "$".join( map( str, [ "AES256", iv, encrypted ] ) )
    
    def decrypt( self, data ):
        """
            Decrypt the data passed in parameter with AES.

            :param data: Data to encrypt
            :type data: str

            :return: Encrypted data
            :rtype: str
        """
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
