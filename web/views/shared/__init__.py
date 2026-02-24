#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import request, current_app, jsonify
from flask import Blueprint

import config
import utils

shared_view = Blueprint( "shared", __name__, template_folder = "templates" )

@shared_view.route( "/add_new_field", methods = [ "POST" ] )
@utils.decorator.login_required
def add_new_field():
    """
        Add a new mark surface to the database.
    """
    new_field = request.form.get( "field" )
    new_field_name = request.form.get( "field_name" )
    
    corr = {
        "surface": "surfaces",
        "activity": "activities"
    }
    table = corr.get( new_field_name, False )

    if table != False:
        current_app.logger.info( "Add '{}' to the {} database".format( new_field, new_field_name ) )
        
        sql = utils.sql.sql_insert_generate( table, "name", "id" )
        current_app.logger.info( sql )
        field_id = config.db.query_fetchone( sql, ( new_field, ) )[ "id" ]
        
        return jsonify( {
            "error": False,
            "id": field_id
        } )

    else:
        return jsonify( {
            "error": True
        } )
    
