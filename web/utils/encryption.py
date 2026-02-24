#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import time

from flask import session

import config
from . import aes
from . import hash
from . import rand

def do_encrypt_dek( data, submission_id ):
    """
        AES decrypt the data with the Data Encryption Key related to the donor.

        :param data: Data to be encrypted
        :type outres: str
        
        :param submission_id: UUID of the submission
        :type outres: str
        
        :return: Encrypted data
        :rtype: str
    """
    dek = get_dek_from_submissionid( submission_id )
    return aes.do_encrypt( data, dek )

def get_dek_from_submissionid( submission_id ):
    """
        Get the Data Encryption Key related to a submission id folder.
        
        :param submission_id: uuid of the submission
        :type submission_id: str
        
        :return: DEK for the submission UUID
        :rtype: str
    """
    try:
        sql = """
            SELECT donor_dek.dek
            FROM donor_dek
            LEFT JOIN users ON users.username = donor_dek.donor_name
            LEFT JOIN submissions ON submissions.donor_id = users.id
            WHERE submissions.uuid = %s
            LIMIT 1
        """
        dek = config.db.query_fetchone( sql, ( submission_id, ) )[ "dek" ]
        if dek == None:
            raise Exception( "no DEK" )
        else:
            return dek
    
    except:
        try:
            return session[ "dek_{}".format( submission_id ) ]
        
        except:
            return None

def do_decrypt_dek( data, submission_id ):
    """
        AES encrypt the data with the Data Encryption Key related to the donor.
        
        :param data: Data to be decrypted
        :type data: str

        :param submission_id: UUID of the submission
        :type submission_id: str

        :return: Decrypted data
        :rtype: str
    """
    dek = get_dek_from_submissionid( submission_id )
    return aes.do_decrypt( data, dek )

def dek_check( submission_id ):
    """
        Check if the DEK is present or can be generated based upon the
        informations present in the database.

        :param submission_id: UUID of the submission to check
        :type submission_id: str

        :return: Is the DEK constructible/present
        :rtype: boolean
    """
    if dek_exists( submission_id ):
        return True
    
    else:
        try:
            return dek_submitte_recreate_session( submission_id )
        except:
            return False

def dek_exists( submission_id ):
    """
        Checks if the DEK is present for the submission_id.

        :param submission_id: UUID of the submission
        :type submission_id: str
    """
    if get_dek_from_submissionid( submission_id ) == None:
        return False
    else:
        return True

def dek_submitte_recreate_session( submission_id ):
    """
        Recreate the DEK key for the time of the session. This function is only
        used to recreate for the submitter a deleted DEK.
        
        :param submission_id: UUID of the submission
        :type submission_id: str
        
        :return: reconstructed DEK
        :rtype: str
    """
    sql = """
        SELECT
            donor_dek.salt,
            donor_dek.dek_check,
            donor_dek.donor_name as username,
            submissions.email_aes as email
        FROM donor_dek
        LEFT JOIN users ON users.username = donor_dek.donor_name
        LEFT JOIN submissions ON submissions.donor_id = users.id
        WHERE submissions.uuid = %s
        LIMIT 1
    """
    user = config.db.query_fetchone( sql, ( submission_id, ) )
    
    username = user[ "username" ]
    email = do_decrypt_user_session( user[ "email" ] )
    dek_salt = user[ "salt" ]
    
    _, dek, _ = dek_generate( username = username, email = email, salt = dek_salt )
    
    to_check = aes.do_decrypt( user[ "dek_check" ], dek )
    to_check = json.loads( to_check )
    
    if to_check[ "value" ] == "ok":
        session[ "dek_{}".format( submission_id ) ] = dek
        return True
    
    else:
        return False

def dek_generate( **kwargs ):
    """
        Generate the DEK based upon the informations passed as arguments.

        :param email: Email of the donor. Exclusive with `email_hash`.
        :type email: str

        :param email_hash: Hash of the email of the donor. Exclusive with `email`.
        :type email_hash: str
        
        :param username: Username of the donor.
        :type username: str
        
        :param salt: Salt used for the key generation (optional).
        :type salt: str
        
        :return: Tuple of the salt, dek and dek_check
        :rtype: tuple
    """
    if "email" in kwargs:
        email = kwargs[ "email" ]
        email = hash.pbkdf2( email, "icnml_user_DEK" ).hash( True )
    elif "email_hash" in kwargs:
        email = kwargs[ "email_hash" ]
    else:
        raise Exception( "need the email or hashed_email" )
    
    if "username" in kwargs:
        username = kwargs[ "username" ]
    else:
        raise Exception( "need the username" )
    
    dek_salt = kwargs.get( "salt", rand.random_data( config.DEK_SALT_LENGTH ) )
    dek = hash.pbkdf2( 
        "{}:{}".format( username, email, ),
        dek_salt,
        iterations = config.DEK_NB_ITERATIONS,
        hash_name = "sha512"
    ).hash( True )
    
    check = {
        "value": "ok",
        "time": int( time.time() * 1000 ),
        "random": rand.random_data( config.DEK_CHECK_SALT_LENGTH )
    }
    check = json.dumps( check )
    check = aes.do_encrypt( check, dek )
    
    return dek_salt, dek, check

################################################################################
#    Decrypt/Encrypt user session

def do_decrypt_user_session( data ):
    """
        Decrypt data with the session_related password for the user. The
        password is automatically retrieved for the current user from the
        `flask.session` variable.
        
        :param data: Data to be decrypted
        :type data: str

        :return: Decrypted data
        :rtype: str
    """
    return aes.do_decrypt( data, session[ "password" ] )

def do_encrypt_user_session( data ):
    """
        Encrypt data with the session_related password for the user. The
        password is automatically retrieved for the current user from the
        `flask.session` variable.
        
        :param data: Data to be encrypted
        :type data: str

        :return: Encrypted data
        :rtype: str
    """
    return aes.do_encrypt( data, session[ "password" ] )

