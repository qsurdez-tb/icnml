#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import config

tables_with_uuid = [
    "cnm_annotation",
    "cnm_candidate",
    "cnm_folder",
    "cnm_result",
    "exercises",
    "files",
    "files_segments",
    "submissions",
]

def get_all_uuid():
    lst = {}
    
    for table in tables_with_uuid:
        for u in config.db.query_fetchall( "SELECT uuid FROM {}".format( table ) ):
            lst[ u[ "uuid" ] ] = table
    
    return lst

def get_all_uuid_partial():
    lst = get_all_uuid()
    lst = [ k[ 0:18 ] for k in lst.keys() ]
    lst.sort()
    return lst

def get_table_for_uuid( uuid ):
    for table in tables_with_uuid:
        sql = "SELECT count( uuid ) AS nb FROM {} WHERE uuid = %s".format( table, )
        nb = config.db.query_fetchone( sql, ( uuid, ) )[ "nb" ]
        if nb == 1:
            return table
    
    else:
        return None

