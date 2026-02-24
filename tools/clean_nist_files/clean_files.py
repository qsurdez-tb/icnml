#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

from NIST import NISTf

input_directory = "/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/input"
output_directory = "/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/output"

for file_name in os.listdir( input_directory ):
    print( "cleaning the file {}".format( file_name ) )
    
    nist_file = NISTf( "{}/{}".format( input_directory, file_name ) )
    
    # Type 1, overwrite of the fiels 1.005 and 1.008, deletion of the field 1.014
    nist_file.set_field( "1.005", "19700101" )
    nist_file.set_field( "1.008", "ICNML" )
    
    try:
        nist_file.delete_tag( "1.014" )
    except:
        pass
    
    # Type2, deletion of all informations
    for tagid in nist_file.get_tagsid( 2 ):
        if tagid > 2:
            nist_file.delete_tag( ( 2, tagid ) )
    
    # Type10 deletion
    try:
        nist_file.delete_ntype( 10 )
    except:
        pass
    
    nist_file.write( "{}/{}".format( output_directory, file_name ) )
    
