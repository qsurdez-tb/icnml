import config
import functions

import MDmisc
import PiAnoS

from base64 import b64decode

### Establish connections

icnml_db = MDmisc.database.Database( config.DB_ICNML_URL )
pianos_db = PiAnoS.Database( config.DB_PIANOS_URL )

### Select print and user for selection team - call two functions of Pianos

print_id = pianos_db.get_print_id( "empty-PRINT" )
print print_id

user_group = pianos_db.get_user_group_id( "Selection" )
print user_group
        
### SQL request to download the cases containing segments

sql = """
    SELECT
        submissions.id,
        users.username,
        files_segments.id AS fid,
        files_segments.pc,
        files_segments.uuid AS segmentuuid,
        files.resolution,
        files.format,
        donor_dek.dek
    FROM submissions
    LEFT JOIN users ON submissions.donor_id = users.id
    LEFT JOIN files ON files.folder = submissions.id
    LEFT JOIN files_segments ON files_segments.tenprint = files.uuid
    LEFT JOIN donor_dek ON donor_dek.donor_name = users.username
    WHERE
        pc IS NOT NULL AND
        files.format NOT LIKE 'NIST'
    ORDER BY files_segments.id ASC
"""
q = icnml_db.query( sql )

### Loop on each segment obtained

for s in q:
    resolution = s[ "resolution" ]
    pc = s[ "pc" ]  # pc is the position code (on the tenprint as per NIST standard)
    
    submissionName = s[ "username" ]
    submissionName = submissionName.replace( "donor", "submission" )
    submissionName = submissionName.replace( "_", " " )
    caseName = "{} segment {}".format( submissionName, pc )
    
    # Test if case exists, if the case already exists, we skip
    try:
        d = pianos_db.get_exercise_id( name = caseName )
        
        continue
    # when the case (caseName) does not exist in PiAnoS we go through except 
    except:
        print caseName
        
        data = icnml_db.query_fetchone(
            "SELECT data FROM files_segments WHERE uuid = %s",
            ( s[ "segmentuuid" ], )
        )[ "data" ]
        data = functions.do_decrypt( data, s[ "dek" ] ) #decrypt the data
        data = functions.str2img( data ) #image in python (pil)
        
        folder_id = pianos_db.create_folder( name = submissionName )
        pianos_db.commit()
        print folder_id #check of the state of loop
        
        exerciseId = pianos_db.create_exercise(
            folder_id = folder_id,
            name = caseName,
            description = caseName,
            mark = data,
            mark_resolution = resolution,
            _print = print_id,
            _print_resolution = resolution
        )
        pianos_db.set_security( folder_id, user_group )
        pianos_db.commit()
    
###

pianos_db.commit()

