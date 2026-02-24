#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def sql_insert_generate( table, fields, returning = None ):
    """
        Generate the SQL `INSERT` query for a table passed in parameter.
        The list of fields shall be provided.
        The field to get back can be specified in the `returning` parameter.

        :param table: Table to insert into
        :type table: string

        :param fields: List (or string) column name
        :type fields: list, tuple or single string (for only one field)
        
        :param returning: Field to return once the insertion done
        :type returning: str

        :return: Insertion query
        :rtype: str
    """
    if isinstance( fields, ( str ) ):
        fields = [ fields ]
    
    if not isinstance( fields, ( list, tuple, ) ):
        raise Exception( "list or tuple needed as fields" )
    
    f = ",".join( fields )
    place_holder = ",".join( [ "%s" ] * len( fields ) )
    sql = "INSERT INTO {} ({}) VALUES ({})".format( table, f, place_holder )
    
    if returning != None:
        sql += " RETURNING {}".format( returning )
        
    return sql
