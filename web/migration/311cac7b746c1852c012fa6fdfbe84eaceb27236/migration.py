#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###

import uuid
import MDmisc.database

###

db_url_in = "pgsql://icnml:icnml@127.0.0.1/icnml"
db_in = MDmisc.database.Database( db_url_in )

db_url_out = "pgsql://icnml:icnml@127.0.0.1/icnml"
db_out = MDmisc.database.Database( db_url_out )

###

sql = """
    SELECT
        cnm_annotation_old.uuid,
        cnm_annotation_old.fpc,
        submissions.donor_id,
        users.username
            
    FROM cnm_annotation_old
    LEFT JOIN cnm_folder_old ON cnm_annotation_old.folder = cnm_folder_old.uuid
    LEFT JOIN submissions ON cnm_folder_old.donor = submissions.uuid
    LEFT JOIN users ON submissions.donor_id = users.id
"""

for r in db_in.query_fetchall( sql ):
    annotation_uuid = r[ "uuid" ]
    donor_id = r[ "donor_id" ]
    pc = r[ "fpc" ]
    username = r[ "username" ]
    
    # Check if the annotation file is already in the target database
    sql = "SELECT count(*) FROM cnm_data WHERE uuid = %s"
    if db_out.query_fetchone( sql, ( annotation_uuid, ) )[ "count" ] != 0:
        continue

    else:
        print username, pc, annotation_uuid
        
        # Get or create the target folder in the `cnm_folder` table
        sql = "SELECT count(*) FROM cnm_folder WHERE donor_id = %s AND pc = %s"
        nb = db_out.query_fetchone( sql, ( donor_id, pc, ) )[ "count" ]
        if nb == 0:
            folder_uuid = str( uuid.uuid4() )
            sql = "INSERT INTO cnm_folder ( donor_id, pc, uuid ) VALUES ( %s, %s, %s ) RETURNING id;"
            db_out.query_fetchone( sql, ( donor_id, pc, folder_uuid ) )
            db_out.commit()
        
        else:
            sql = "SELECT uuid FROM cnm_folder WHERE donor_id = %s AND pc = %s"
            folder_uuid = db_out.query_fetchone( sql, ( donor_id, pc, ) )[ "uuid" ]
            
        # Get the annotation field
        sql = "SELECT annotation_data FROM cnm_annotation_old WHERE uuid = %s"
        data = db_in.query_fetchone( sql, ( annotation_uuid, ) )[ "annotation_data" ]
        
        # Copy the data over to the new table
        sql = "INSERT INTO cnm_data ( uuid, folder_uuid, data, type_id ) VALUES ( %s, %s, %s, %s ) RETURNING id;"
        db_out.query( sql, ( annotation_uuid, folder_uuid, data, 1 ) )
        db_out.commit()

