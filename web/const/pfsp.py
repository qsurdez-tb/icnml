#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from _collections import defaultdict

zones = [
    # F1
    {
        "sel": [ "F1-tip" ],
        "zone": "tip",
        "lat": "right",
        "desc": "Right thumb tip",
        "coords": "664,341,650,390,631,370,650,337",
    },
    {
        "sel": [ "F1-distal" ],
        "zone": "distal",
        "lat": "right",
        "desc": "Right thumb distal",
        "coords": "748,386,716,358,684,345,664,344,659,364,654,383,682,406,696,424,705,446",
    },
    
    {
        "sel": [ "F1-proximal" ],
        "zone": "proximal",
        "lat": "right",
        "desc": "Right thumb proximal",
        "coords": "823,433,806,432,759,389,750,385,708,446,756,493,771,520,805,543",
    },
    
    # F2
    {
        "sel": [ "F2-tip" ],
        "zone": "tip",
        "lat": "right",
        "desc": "Right index tip",
        "coords": "778,85,757,93,737,104,732,81,771,67",
    },
    {
        "sel": [ "F2-distal" ],
        "zone": "distal",
        "lat": "right",
        "desc": "Right index distal",
        "coords": "803,146,785,99,776,87,757,93,742,102,746,129,747,148,757,163",
    },
    {
        "sel": [ "F2-medial" ],
        "zone": "medial",
        "lat": "right",
        "desc": "Right index medial",
        "coords": "804,149,834,208,783,239,777,223,754,167",
    },
    {
        "sel": [ "F2-proximal" ],
        "zone": "proximal",
        "lat": "right",
        "desc": "Right index proximal",
        "coords": "837,211,857,244,873,277,815,312,794,275,789,239",
    },
    
    # F3
    {
        "sel": [ "F3-tip" ],
        "zone": "tip",
        "lat": "right",
        "desc": "Right middle tip",
        "coords": "899,28,873,30,854,36,852,13,898,9",
    },
    {
        "sel": [ "F3-distal" ],
        "zone": "distal",
        "lat": "right",
        "desc": "Right middle distal",
        "coords": "913,94,902,42,897,30,876,31,859,36,855,60,859,82,861,104",
    },
    {
        "sel": [ "F3-medial" ],
        "zone": "medial",
        "lat": "right",
        "desc": "Right middle medial",
        "coords": "912,96,934,173,877,188,865,154,860,107",
    },
    {
        "sel": [ "F3-proximal" ],
        "zone": "proximal",
        "lat": "right",
        "desc": "Right middle proximal",
        "coords": "934,175,949,222,954,256,897,270,889,238,879,189",
    },
    
    # F4
    {
        "sel": [ "F4-tip" ],
        "zone": "tip",
        "lat": "right",
        "desc": "Right ring tip",
        "coords": "1003,53,983,51,966,57,953,74,955,32,1001,28",
    },
    {
        "sel": [ "F4-distal" ],
        "zone": "distal",
        "lat": "right",
        "desc": "Right ring distal",
        "coords": "1012,115,1006,63,993,53,980,52,967,58,958,81,960,118",
    },
    {
        "sel": [ "F4-medial" ],
        "zone": "medial",
        "lat": "right",
        "desc": "Right ring",
        "coords": "1010,118,1022,190,965,194,960,156,959,122",
    },
    {
        "sel": [ "F4-proximal" ],
        "zone": "proximal",
        "lat": "right",
        "desc": "Right ring proximal",
        "coords": "1027,271,1028,221,1022,192,967,197,961,226,967,260",
    },
    
    # F5
    {
        "sel": [ "F5-tip" ],
        "zone": "tip",
        "lat": "right",
        "desc": "Right little tip",
        "coords": "1127,142,1088,145,1086,127,1127,125",
    },
    {
        "sel": [ "F5-distal" ],
        "zone": "distal",
        "lat": "right",
        "desc": "Right little distal",
        "coords": "1125,211,1128,193,1125,146,1104,144,1086,151,1081,182,1080,206",
    },
    {
        "sel": [ "F5-medial" ],
        "zone": "medial",
        "lat": "right",
        "desc": "Right little medial",
        "coords": "1117,270,1124,213,1077,204,1068,251",
    },
    {
        "sel": [ "F5-proximal" ],
        "zone": "proximal",
        "lat": "right",
        "desc": "Right little proximal",
        "coords": "1108,328,1114,295,1118,274,1067,254,1058,272,1050,294",
    },
    
    # F6
    {
        "sel": [ "F6-tip" ],
        "zone": "tip",
        "lat": "left",
        "desc": "Left thumb tip",
        "coords": "579,341,593,390,612,370,593,337",
    },
    {
        "sel": [ "F6-distal" ],
        "zone": "distal",
        "lat": "left",
        "desc": "Left thumb distal",
        "coords": "495,386,527,358,559,345,579,344,584,364,589,383,561,406,547,424,538,446",
    },
    {
        "sel": [ "F6-proximal" ],
        "zone": "proximal",
        "lat": "left",
        "desc": "Left thumb proximal",
        "coords": "420,433,437,432,484,389,493,385,535,446,487,493,472,520,438,543",
    },
    
    # F7
    {
        "sel": [ "F7-tip" ],
        "zone": "tip",
        "lat": "left",
        "desc": "Left index tip",
        "coords": "465,85,486,93,506,104,511,81,472,67",
    },
    {
        "sel": [ "F7-distal" ],
        "zone": "distal",
        "lat": "left",
        "desc": "Left index distal",
        "coords": "440,146,458,99,467,87,486,93,501,102,497,129,496,148,486,163",
    },
    {
        "sel": [ "F7-medial" ],
        "zone": "medial",
        "lat": "left",
        "desc": "Left index medial",
        "coords": "439,149,409,208,460,239,466,223,489,167",
    },
    {
        "sel": [ "F7-proximal" ],
        "zone": "proximal",
        "lat": "left",
        "desc": "Left index proximal",
        "coords": "406,211,386,244,370,277,428,312,449,275,454,239",
    },
    
    # F8
    {
        "sel": [ "F8-tip" ],
        "zone": "tip",
        "lat": "left",
        "desc": "Left middle tip",
        "coords": "344,28,370,30,389,36,391,13,345,9",
    },
    {
        "sel": [ "F8-distal" ],
        "zone": "distal",
        "lat": "left",
        "desc": "Left middle distal",
        "coords": "330,94,341,42,346,30,367,31,384,36,388,60,384,82,382,104",
    },
    {
        "sel": [ "F8-medial" ],
        "zone": "medial",
        "lat": "left",
        "desc": "Left middle medial",
        "coords": "331,96,309,173,366,188,378,154,383,107",
    },
    {
        "sel": [ "F8-proximal" ],
        "zone": "proximal",
        "lat": "left",
        "desc": "Left middle proximal",
        "coords": "309,175,294,222,289,256,346,270,354,238,364,189",
    },
    
    # F9
    {
        "sel": [ "F9-tip" ],
        "zone": "tip",
        "lat": "left",
        "desc": "Left ring tip",
        "coords": "240,53,260,51,277,57,290,74,288,32,242,28",
    },
    {
        "sel": [ "F9-distal" ],
        "zone": "distal",
        "lat": "left",
        "desc": "Left ring distal",
        "coords": "231,115,237,63,250,53,263,52,276,58,285,81,283,118",
    },
    {
        "sel": [ "F9-medial" ],
        "zone": "medial",
        "lat": "left",
        "desc": "Left ring medial",
        "coords": "233,118,221,190,278,194,283,156,284,122",
    },
    {
        "sel": [ "F9-proximal" ],
        "zone": "proximal",
        "lat": "left",
        "desc": "Left ring proximal",
        "coords": "216,271,215,221,221,192,276,197,282,226,276,260",
    },
    
    # F10
    {
        "sel": [ "F10-tip" ],
        "zone": "tip",
        "lat": "left",
        "desc": "Left little tip",
        "coords": "116,142,155,145,157,127,116,125",
    },
    {
        "sel": [ "F10-distal" ],
        "zone": "distal",
        "lat": "left",
        "desc": "Left little distal",
        "coords": "118,211,115,193,118,146,139,144,157,151,162,182,163,206",
    },
    {
        "sel": [ "F10-medial" ],
        "zone": "medial",
        "lat": "left",
        "desc": "Left little medial",
        "coords": "126,270,119,213,166,204,175,251",
    },
    {
        "sel": [ "F10-proximal" ],
        "zone": "proximal",
        "lat": "left",
        "desc": "Left little proximal",
        "coords": "135,328,129,295,125,274,176,254,185,272,193,294",
    },
    
    # Grasps
    {
        "sel": [ "Left-grasp" ],
        "zone": "grasp",
        "lat": "left",
        "desc": "Left grasp",
        "coords": "493,314,513,368,485,392,452,421,419,437,412,377,423,321,453,280",
    },
    {
        "sel": [ "Right-grasp" ],
        "zone": "grasp",
        "lat": "right",
        "desc": "Right grasp",
        "coords": "750,314,730,368,758,392,791,421,824,437,831,377,820,321,790,280",
    },
    
    # Carpal delta area
    {
        "sel": [ "Left-carpal_delta_area" ],
        "zone": "carpal_delta_area",
        "lat": "left",
        "desc": "Left carpal delta area",
        "coords": "339,612,146,598,146,568,329,580",
    },
    {
        "sel": [ "Right-carpal_delta_area" ],
        "zone": "carpal_delta_area",
        "lat": "right",
        "desc": "Right carpal delta area",
        "coords": "904,612,1097,598,1097,568,914,580",
    },
    
    # Wrist bracelets
    {
        "sel": [ "Left-wrist_bracelet" ],
        "zone": "wrist_bracelet",
        "lat": "left",
        "desc": "Left wrist bracelet",
        "coords": "118,594,322,616,326,634,98,630",
    },
    {
        "sel": [ "Right-wrist_bracelet" ],
        "zone": "wrist_bracelet",
        "lat": "right",
        "desc": "Right wrist bracelet",
        "coords": "1125,594,921,616,917,634,1145,630",
    },
    
    # Lower Palm
    {
        "sel": [ "Left-thenar" ],
        "zone": "thenar",
        "lat": "left",
        "desc": "Left thenar",
        "coords": "228,572,329,581,344,607,392,585,435,548,409,380,339,390,274,419,240,455,222,506",
    },
    {
        "sel": [ "Right-thenar" ],
        "zone": "thenar",
        "lat": "right",
        "desc": "Right thenar",
        "coords": "1015,572,914,581,899,607,851,585,808,548,834,380,904,390,969,419,1003,455,1021,506",
    },
    {
        "sel": [ "Left-hypothenar" ],
        "zone": "hypothenar",
        "lat": "left",
        "desc": "Left hypothenar",
        "coords": "147,564,144,491,148,407,255,437,221,502,226,574",
    },
    {
        "sel": [ "Right-hypothenar" ],
        "zone": "hypothenar",
        "lat": "right",
        "desc": "Right hypothenar",
        "coords": "1096,564,1099,491,1095,407,988,437,1022,502,1017,574",
    },
    {
        "sel": [ "Left-interdigital" ],
        "zone": "interdigital",
        "lat": "left",
        "desc": "Left interdigital",
        "coords": "411,371,423,313,356,275,288,259,199,278,258,429,300,399,353,382"
    },
    {
        "sel": [ "Right-interdigital" ],
        "zone": "interdigital",
        "lat": "right",
        "desc": "Right interdigital",
        "coords": "832,371,820,313,887,275,955,259,1044,278,985,429,943,399,890,382"
    },
    {
        "sel": [ "Left-interdigital", "Left-hypothenar" ],
        "zone": "interdigitalhypothenar",
        "lat": "left",
        "desc": "Left interdigital and hypothenar",
        "coords": "134,335,203,292,256,434,148,405",
    },
    {
        "sel": [ "Right-interdigital", "Right-hypothenar" ],
        "zone": "interdigitalhypothenar",
        "lat": "right",
        "desc": "Right interdigital and hypothenar",
        "coords": "1109,335,1040,292,987,434,1095,405",
    },
    {
        "sel": [ "Left-writer_palm" ],
        "zone": "writer_palm",
        "lat": "left",
        "desc": "Left writer palm",
        "coords": "98,308,130,312,148,394,146,466,145,525,145,576,123,574,98,569",
    },
    {
        "sel": [ "Right-writer_palm" ],
        "zone": "writer_palm",
        "lat": "right",
        "desc": "Right writer palm",
        "coords": "1145,308,1113,312,1095,394,1097,466,1098,525,1098,576,1120,574,1145,569",
    },
    
    # Multi-"zone"s
    {
        "sel": [
            "F6-distal", "F6-proximal",
            "F7-distal", "F7-medial", "F7-proximal",
            "F8-distal", "F8-medial", "F8-proximal",
            "F9-distal", "F9-medial", "F9-proximal",
            "F10-distal", "F10-medial", "F10-proximal",
            "Left-writer_palm", "Left-grasp", "Left-carpal_delta_area", "Left-wrist_bracelet",
            "Left-hypothenar", "Left-thenar", "Left-interdigital"
        ],
        "lat": "left",
        "desc": "Left full palm",
        "coords": "39,640,-6,636,0,17,42,19",
    },
    {
        "sel": [
            "F1-distal", "F1-proximal",
            "F2-distal", "F2-medial", "F2-proximal",
            "F3-distal", "F3-medial", "F3-proximal",
            "F4-distal", "F4-medial", "F4-proximal",
            "F5-distal", "F5-medial", "F5-proximal",
            "Right-writer_palm", "Right-grasp", "Right-carpal_delta_area", "Right-wrist_bracelet",
            "Right-hypothenar", "Right-thenar", "Right-interdigital"
        ],
        "lat": "right",
        "desc": "Right full palm",
        "coords": "1204,640,1249,636,1243,17,1201,19",
    },
     
    {
        "sel": [
            "Left-writer_palm", "Left-carpal_delta_area", "Left-wrist_bracelet",
            "Left-hypothenar", "Left-thenar", "Left-interdigital"
        ],
        "lat": "left",
        "desc": "Left lower palm",
        "coords": "78,638,45,638,42,292,77,294",
    },
    {
        "sel": [
            "Right-writer_palm", "Right-carpal_delta_area", "Right-wrist_bracelet",
            "Right-hypothenar", "Right-thenar", "Right-interdigital"
        ],
        "lat": "right",
        "desc": "Right lower palm",
        "coords": "1165,638,1198,638,1201,292,1166,294",
    },
     
    {
        "sel": [
            "F6-distal", "F6-proximal",
            "F7-distal", "F7-medial", "F7-proximal",
            "F8-distal", "F8-medial", "F8-proximal",
            "F9-distal", "F9-medial", "F9-proximal",
            "F10-distal", "F10-medial", "F10-proximal",
        ],
        "lat": "left",
        "desc": "Left upper palm",
        "coords": "78,292,42,290,46,18,63,18,63,90,75,91",
    },
    {
        "sel": [
            "F1-distal", "F1-proximal",
            "F2-distal", "F2-medial", "F2-proximal",
            "F3-distal", "F3-medial", "F3-proximal",
            "F4-distal", "F4-medial", "F4-proximal",
            "F5-distal", "F5-medial", "F5-proximal",
        ],
        "lat": "right",
        "desc": "Right upper palm",
        "coords": "1165,292,1201,290,1197,18,1180,18,1180,90,1168,91",
    },
     
    {
        "sel": [
            "F6-tip", "F7-tip", "F8-tip", "F9-tip", "F10-tip"
        ],
        "lat": "left",
        "desc": "Left tips",
        "coords": "101,89,66,87,65,20,102,20",
    },
    {
        "sel": [
            "F1-tip", "F2-tip", "F3-tip", "F4-tip", "F5-tip"
        ],
        "lat": "right",
        "desc": "Right tips",
        "coords": "1142,89,1177,87,1178,20,1141,20",
    },
]

# PFSP zones to fpc
pfsp2fpc = defaultdict( list )
for pfc in [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]:
    for loc in [ "tip", "distal" ]:
        pfsp2fpc[ "F{}-{}".format( pfc, loc ) ].append( pfc )

pfsp2fpc[ "F1-tip" ].append( 11 )
pfsp2fpc[ "F1-distal" ].append( 11 )
pfsp2fpc[ "F6-tip" ].append( 12 )
pfsp2fpc[ "F6-distal" ].append( 12 )

for fpc in [ 2, 3, 4, 5 ]:
    for z in [ "tip", "distal" ]:
        pfsp2fpc[ "F{}-{}".format( fpc, z ) ].append( 13 )
for fpc in [ 7, 8, 9, 10 ]:
    for z in [ "tip", "distal" ]:
        pfsp2fpc[ "F{}-{}".format( fpc, z ) ].append( 14 )

for side, fpc in [ ( "Right", 25 ), ( "Left", 27 ) ]:
    for z in [ "grasp", "carpal_delta_area", "wrist_bracelet", "thenar", "hypothenar", "interdigital", "writer_palm" ]:
        pfsp2fpc[ "{}-{}".format( side, z ) ].append( fpc )

pfsp2fpc[ "Right-writer_palm" ].append( 22 )
pfsp2fpc[ "Left-writer_palm" ].append( 24 )

# fpc to PFSP
fpc2pfsp = defaultdict( list )
for fpc in [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ]:
    for loc in [ "tip", "distal" ]:
        fpc2pfsp[ fpc ].append( "F{}-{}".format( fpc, loc ) )

for side, fpc in [ ( "Right", 25 ), ( "Left", 27 ) ]:
    for z in [ "grasp", "carpal_delta_area", "wrist_bracelet", "thenar", "hypothenar", "interdigital", "writer_palm" ]:
        fpc2pfsp[ fpc ].append( "{}-{}".format( side, z ) )

# PFSP code friendly name
pfspdesc = {}
n = 1
for laterality in [ "right", "left" ]:
    for finger in [ "thumb", "index", "middle", "ring", "little" ]:
        for zone in [ "tip", "distal", "medial", "proximal" ]:
            pfspdesc[ "F{}-{}".format( n, zone ) ] = "{} {} {}".format( laterality, finger, zone )
        n += 1

# PFSP to donor general pattern search
pfsp_fpc_search = {}
n = 1
for laterality in [ "right", "left" ]:
    for finger in [ "thumb", "index", "middle", "ring", "little" ]:
        for zone in [ "tip", "distal" ]:
            pfsp_fpc_search[ "F{}-{}".format( n, zone ) ] = "{}".format( n )
        n += 1

