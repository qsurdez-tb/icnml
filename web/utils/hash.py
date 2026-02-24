#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import binascii
import hashlib

from . import rand

class pbkdf2( object ):
    """
        Class to generate and handle PBKDF2 hash. This class is only a nice
        wrapper arrount the `hashlib.pbkdf2_hmac` function.
        
        :param word: Main input of the pbkdf2 class. This can be a word to hash or a hashed string (starting with `pbkdf2$`)
        :type word: str

        :param salt: Salt to use for the hashing function OR the stored hash (if starting with 'pbkdf2$')
        :type salt: str
        
        :param iterations: Number of iterations to do in the hashing process. Default value set to 20'000 iterations
        :type iterations: int

        :param hash_name: Hashing function to use in the pbkdf2 process. Default value set to `sha512`
        :type hash_name: str
        
        Usage:

            >>> h = utils.hash.pbkdf2( word = "password", salt = "salt", iterations = 100000, hash_name = "sha512" )
            >>> h.hash( hash_only = True )
            'f5d17022c96af46c0a1dc49a58bbe654a28e98104883e4af4de974cda2c74122dd082f4105a93fc80692ca4eb1a784cfeda81bfaa33f5192cc9143d818bd7581'
            >>> h.hash()
            'pbkdf2$sha512$salt$100000$f5d17022c96af46c0a1dc49a58bbe654a28e98104883e4af4de974cda2c74122dd082f4105a93fc80692ca4eb1a784cfeda81bfaa33f5192cc9143d818bd7581'
    """
    def __init__( self, word, salt = None, iterations = 20000, hash_name = "sha512" ):
        if salt != None and salt.startswith( "pbkdf2$" ):
            self.word = word
            self.stored_hash = salt
            _, self.hash_name, self.salt, self.iterations, self.h = salt.split( "$" )
            self.iterations = int( self.iterations )
        
        else:
            self.word = word
            self.salt = salt or rand.random_data( 100 )
            self.iterations = int( iterations )
            self.hash_name = hash_name
            self.stored_hash = None
            self.h = None
    
    def hash( self, hash_only = False ):
        """
            Get the hash of the `self.word` variable. All the parameters are
            set in the `self.__init__()` function before-hand.

            This function can be used to compute the hash only (`hash_only = True`) or return the hash with the parameters (hash name, salt, iterations, ...).
        """
        h = hashlib.pbkdf2_hmac( self.hash_name, self.word, self.salt, self.iterations )
        h = binascii.hexlify( h )
        
        if hash_only:
            return h
        else:
            return "$".join( map( str, [ "pbkdf2", self.hash_name, self.salt, self.iterations, h ] ) )
    
    def verify( self, stored_hash = None ):
        """
            Only used to check the input against some pre-computed value. This
            has to be used to compare password for example.
            
            :param stored_hash: Hash to compare against (optional)
            :type stored_hash: str
            
            Usage:
            
                >>> data = "data"
                >>> data_stored = utils.hash.pbkdf2( data, "salt", 100000 ).hash()
                >>> utils.hash.pbkdf2( data, data_stored ).verify()
                True
                >>> utils.hash.pbkdf2( data ).verify( data_stored )
                True
        """
        if stored_hash == None:
            return self.stored_hash == self.hash()
        
        else:
            _, self.hash_name, self.salt, self.iterations, self.h = stored_hash.split( "$" )
            self.iterations = int( self.iterations )
            
            return stored_hash == self.hash()
        
