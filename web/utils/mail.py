#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import smtplib

import config

class mySMTP( object ):
    def __init__( self ):
        self.host = config.smtpserver
        self.port = config.smtpport
        self.username = config.smtpuser
        self.password = config.smtppassword
        self.sender = config.sender
    
    def __enter__( self ):
        self.s = smtplib.SMTP( self.host, self.port )
        self.s.starttls()
        self.s.login( self.username, self.password )
        return self.s
    
    def __exit__( self, ty, value, traceback ):
        self.s.quit()
        
