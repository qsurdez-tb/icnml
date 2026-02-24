#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import session, render_template, url_for
import jinja2
import json

import config
import utils
import version

@utils.redis.redis_cache( 10 )
def sent_app_files_auto():
    """
        Generate the list of files to be included in the flask app.
        This will generate the correct HTML code to include a `.js` or a `.css` file.
        The value returned by this function can be directly included in the html file to be rendered.
        
        :return: HTML to be included in the jinja template
        :rtype: str
    """
    def tmp_sent_app_file_auto_inner( route, files ):
        im = {
            'js': '<script type="text/javascript" src="{}"></script>',
            'css': '<link type="text/css" rel="stylesheet" href="{}">'
        }
        
        ret = []
        for f in files:
            ext = f.split( "." )[ -1 ]
            url = url_for( route, subpath = f, version = version.__commitshort__ )
            ret.append( im[ ext ].format( url ) )
            
        return ret
    
    ret = []
    for route, files in [ ( "files.send_cdn_files", config.cdnfiles ), ( "files.send_app_files", config.appfiles ) ]:
        ret.extend( tmp_sent_app_file_auto_inner( route, files ) )
    
    return "\n".join( ret )

def render_jinja_html( template_loc, file_name, **context ):
    """
        This function will render a jinja template without a `flask` context (for example to render emails).
        The function returns the template rendered as html.

        :param template_loc: Directory containing the jinja template
        :type template_loc: str

        :param file_name: Name of the jinja template file (stored in the `template_loc` directory) 
        :type file_name: str

        :return: HTML of the rendered template
        :rtype: str
        
        Usage:
        
            >>> email_content = utils.template.render_jinja_html( "templates/email", "reset.html", url = url, username = username )
    """
    return jinja2.Environment( 
        loader = jinja2.FileSystemLoader( template_loc + "/" )
    ).get_template( file_name ).render( context )

def my_render_template( *args, **kwargs ):
    """
        Render and returns a jinja/html file provided as template.
        This function is a simple overload of the `flask.render_template` function to add some variables stored in the session and passed as parameters to have them as jinja variables inside the template file.

        The parameters are directly passed to the `flask.render_template` function.
        
        Usage:
        
            >>> my_render_template( "template.html", variables = "value" )
        
    """
    kwargs[ "baseurl" ] = config.baseurl
    kwargs[ "envtype" ] = config.envtype
    kwargs[ "app_files" ] = sent_app_files_auto()
    kwargs[ "account_type" ] = session.get( "account_type", None )
    kwargs[ "account_type_name" ] = session.get( "account_type_name", None )
    kwargs[ "admin" ] = session.get( "account_type_name", None ) == "Administrator"
    kwargs[ "nist_file_extensions" ] = json.dumps( config.NIST_file_extensions )
    
    if session.get( "account_type", False ):
        at = config.account_type_id_name[ session.get( "account_type" ) ]
        kwargs[ "navigation" ] = "navigations/{}.html".format( at.lower() )
    
    kwargs[ "pianosendpoint" ] = config.pianosendpoint
    
    return render_template( *args, **kwargs )
