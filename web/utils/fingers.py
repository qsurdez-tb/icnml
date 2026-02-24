#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def get_multi_img_fpc( fpc ):
    multi_img_fpc = {
        1: [ 1, 11 ],
        2: [ 2, 13 ],
        3: [ 3, 13 ],
        4: [ 4, 13 ],
        5: [ 5, 13 ],
        6: [ 6, 12 ],
        7: [ 7, 14 ],
        8: [ 8, 14 ],
        9: [ 9, 14 ],
        10: [ 10, 14 ]
    }
    fpc = int( fpc )
    fpcs = multi_img_fpc.get( fpc, [ fpc ] )
    
    return fpcs

