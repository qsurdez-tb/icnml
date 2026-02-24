#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import hashlib
import uuid

def derive_uuid_from_uuid( input_uuid, nb = 0 ):
    """
        Derive a UUID from an input UUID and a int order. This allows to
        generate reproducible UUID based upon an input UUID. This function can
        be used to display to the user a UUID that is not the same as the one
        for admins, be we can still find the correspondence if we really need
        to. The output of the function is a UUID in version 3.
        
        >>> imports utils
        >>> input_uuid = "e3e70682-c209-4cac-629f-6fbed82c07cd"
        
        If run multiple times, the same UUID will be produced.

        >>> utils.uuid_utils.derive_uuid_from_uuid( input_uuid, 0 )
        UUID('940ffac2-af8c-3377-9390-a91c06a82fba')
        >>> utils.uuid_utils.derive_uuid_from_uuid( input_uuid, 0 )
        UUID('940ffac2-af8c-3377-9390-a91c06a82fba')
        
        It's possible to generate multiple UUID based upon one input UUID by changing the 'nb' parameter.
        
        >>> utils.uuid_utils.derive_uuid_from_uuid( input_uuid, 1 )
        UUID('4af60b16-6eff-31fb-bca0-080c2ad2c6e3')
    """
    m = hashlib.md5()
    seed = "{}_{}".format( input_uuid, nb )
    
    m.update( seed.encode( "utf-8" ) )
    derived_uuid = uuid.UUID( m.hexdigest(), version = 3 )
    
    return str( derived_uuid )

