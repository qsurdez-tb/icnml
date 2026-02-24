#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
import cPickle
import functools
import hashlib
from cStringIO import StringIO

import config
import version

def redis_cache( ttl = 3600 ):
    """
        Caches the result of the decorated function in redis.
    """
    def decorator( func ):
        @functools.wraps( func )
        def wrapper_cache( *args, **kwargs ):
            lst = []
            lst.append( version.__commitshort__ )
            lst.append( func.__name__ )
            lst.extend( args )
            lst = map( str, lst )
            index = "_".join( lst )
            index = hashlib.sha256( index ).hexdigest()
            
            d = config.redis_dbs[ "cache" ].get( index )
            
            if d != None:
                config.redis_dbs[ "cache" ].expire( index, ttl )
                
                buff = StringIO()
                buff.write( base64.b64decode( d ) )
                buff.seek( 0 )
                
                return cPickle.load( buff )
            
            else:
                d = func( *args, **kwargs )
                
                try:
                    buff = StringIO()
                    cPickle.dump( d, buff )
                    buff.seek( 0 )
                    d_cached = base64.b64encode( buff.getvalue() )

                    config.redis_dbs[ "cache" ].set( index, d_cached, ex = ttl )
                    
                except:
                    pass
                
                return d
    
        return wrapper_cache
    return decorator

