#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import string

def random_data( N ):
    """
        Get a random string of characters.
        
        :param N: Size of the random data
        :type N: int

        :return: Random data
        :rtype: str
    """
    return "".join( random.choice( string.ascii_uppercase + string.digits ) for _ in range( N ) )
