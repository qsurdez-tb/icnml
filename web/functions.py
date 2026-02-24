#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
import cPickle
from cStringIO import StringIO
import functools
import hashlib
import json
import time

from flask.globals import session
from PIL import Image, ImageDraw, ImageFont

import config
import utils

################################################################################
#    Redis Cache

################################################################################
#    No preview image

def no_preview_image( return_pil = False ):
    img = Image.new( "L", ( 210, 297 ), 255 )
    draw = ImageDraw.Draw( img )
    font = ImageFont.truetype( "arial.ttf", 18 )
    draw.text( ( 0, 0 ), "No preview", 0, font = font )
    
    if return_pil:
        return img
    
    else:
        return utils.images.pil2buffer( img, "PNG" )

