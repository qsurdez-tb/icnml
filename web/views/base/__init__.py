#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Blueprint
from flask import jsonify, session, redirect, url_for

import config
import version
import utils

base_view = Blueprint( "base", __name__, template_folder = "templates" )

@base_view.route( "/" )
@utils.decorator.login_required
def home():
    """
        Serve the homepage to all users.
    """
    if session.get( "url_redirect", None ) != None:
        url = session.pop( "url_redirect" )
        return redirect( url )
    
    elif session[ "account_type_name" ] == "Donor":
        return redirect( url_for( "donor.user_myprofile_dek" ) )
    
    elif session[ "account_type_name" ] == "Submitter":
        return redirect( url_for( "submission.submission_list" ) )
    
    elif session[ "account_type_name" ] == "Administrator":
        return redirect( url_for( "submission.admin_submission_list" ) )
    
    elif session[ "account_type_name" ] == "AFIS":
        return redirect( url_for( "afis.list_folders" ) )
    
    elif session[ "account_type_name" ] == "Trainer":
        return redirect( url_for( "trainer.search" ) )
    
    else:
        return utils.template.my_render_template( "base/index.html" )
