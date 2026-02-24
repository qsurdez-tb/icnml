var register_key = async function( e )
{
    e.preventDefault();
    
    var key_name = $( "#keyname" ).val();
    
    try {
        var credentialCreateOptionsFromServer = await $.ajax( {
            url: begin_activate_url,
            dataType: "json",
            method: "POST",
            data: {
                key_name: key_name
            }
        } );
        
    } catch ( err ) {
        return console.error( "Failed to generate credential request options: ", credentialCreateOptionsFromServer )
    }
    
    var publicKeyCredentialCreateOptions = transformCredentialCreateOptions( credentialCreateOptionsFromServer );
    
    try {
        var credential = await navigator.credentials.create( {
            publicKey: publicKeyCredentialCreateOptions
        } );
        
    } catch ( err ) {
        return console.error( "Error creating credential: ", err );
    }
    
    var newAssertionForServer = transformNewAssertionForServer( credential );
    
    try {
        var assertionValidationResponse = await $.ajax( {
            url: verify_url,
            dataType: "json",
            method: "POST",
            data: newAssertionForServer
        } );
        
    } catch ( err ) {
        return console.error( "Server validation of credential failed:", err );
    }
    
    toastr.success( "Key added" );
    
    window.location.reload();
}

var login_key = async function()
{
    var delay_reload = function( v )
    {
        return new Promise( function( resolve ){
            setTimeout( resolve.bind( null, v ), 1000 );
        } ).then( function(){
            window.location.reload();
        } );
    }
    
    try {
        var credentialRequestOptionsFromServer = await $.ajax( {
            url: begin_assertion_url,
            dataType: "json"
        } );
        
        if( credentialRequestOptionsFromServer.error )
            throw credentialRequestOptionsFromServer.message;
        
    } catch( err ) {
        toastr.error( err, "Error when getting request options from server" );
        return delay_reload();
    }
    
    credentialRequestOptionsFromServer = credentialRequestOptionsFromServer.data;
    credentialRequestOptionsFromServer = transformCredentialRequestOptions( credentialRequestOptionsFromServer );
    
    try {
        var assertion = await navigator.credentials.get( {
            publicKey: credentialRequestOptionsFromServer
        } );
        
    } catch ( err ) {
        toastr.error( err, "Error when creating credential" );
        return delay_reload();
    }
    
    var assertion = transformAssertionForServer( assertion );
    
    try {
        var response = await $.ajax( {
            url: verify_assertion_url,
            dataType: "json",
            method: "POST",
            data: assertion
        } );
        
        if( response.error )
            throw response.message;
    
    } catch ( err ) {
        toastr.error( err, "Error when validating assertion on server" );
        return delay_reload();
    }

    toastr.success( "Logged in" );
    
    location.href = homeurl;
}

var b64enc = function(  buf )
{
    return base64js.fromByteArray( buf )
        .replace( /\+/g, "-" )
        .replace( /\//g, "_" )
        .replace( /=/g, "" );
}

var b64RawEnc = function( buf )
{
    return base64js.fromByteArray( buf )
        .replace( /\+/g, "-" )
        .replace( /\//g, "_" );
}

var hexEncode = function( buf )
{
    return Array.from( buf )
        .map( function( x )
        {
            return ( "0" + x.toString( 16 ) ).substr( -2 );
        } )
        .join( "" );
}

var transformCredentialRequestOptions = function( credentialRequestOptionsFromServer )
{
    var { challenge, allowCredentials } = credentialRequestOptionsFromServer;

    challenge = Uint8Array.from( atob( challenge ), c => c.charCodeAt( 0 ) );

    allowCredentials = allowCredentials.map( function( credentialDescriptor )
    {
        var { id } = credentialDescriptor;
        id = id.replace( /\_/g, "/" ).replace( /\-/g, "+" );
        id = Uint8Array.from( atob( id ), function( c ){ return c.charCodeAt( 0 ) } );
        
        return Object.assign( {}, credentialDescriptor, { id } );
    } );

    return Object.assign(
        {},
        credentialRequestOptionsFromServer,
        {
            challenge,
            allowCredentials
        }
    );
};

var transformCredentialCreateOptions = function( credentialCreateOptionsFromServer )
{
    var { challenge, user } = credentialCreateOptionsFromServer;
    user.id = Uint8Array.from(
        atob( credentialCreateOptionsFromServer.user.id ),
        function( c )
        {
            return c.charCodeAt( 0 );
        }
    );
    
    challenge = Uint8Array.from(
        atob( credentialCreateOptionsFromServer.challenge ),
        function( c )
        {
            return c.charCodeAt( 0 );
        }
    );
    
    var transformedCredentialCreateOptions = Object.assign( 
        {},
        credentialCreateOptionsFromServer,
        {
            challenge,
            user
        }
    );
    
    return transformedCredentialCreateOptions;
}

var transformNewAssertionForServer = function( newAssertion )
{
    var attObj = new Uint8Array( newAssertion.response.attestationObject );
    var clientDataJSON = new Uint8Array( newAssertion.response.clientDataJSON );
    var rawId = new Uint8Array( newAssertion.rawId );
    
    var registrationClientExtensions = newAssertion.getClientExtensionResults();
    
    return {
        id: newAssertion.id,
        rawId: b64enc( rawId ),
        type: newAssertion.type,
        attObj: b64enc( attObj ),
        clientData: b64enc( clientDataJSON ),
        registrationClientExtensions: JSON.stringify( registrationClientExtensions )
    };
}

var transformAssertionForServer = function( newAssertion )
{
    var authData = new Uint8Array( newAssertion.response.authenticatorData );
    var clientDataJSON = new Uint8Array( newAssertion.response.clientDataJSON );
    var rawId = new Uint8Array( newAssertion.rawId );
    var sig = new Uint8Array( newAssertion.response.signature );
    var assertionClientExtensions = newAssertion.getClientExtensionResults();

    return {
        id: newAssertion.id,
        rawId: b64enc( rawId ),
        type: newAssertion.type,
        authData: b64RawEnc( authData ),
        clientData: b64RawEnc( clientDataJSON ),
        signature: hexEncode( sig ),
        assertionClientExtensions: JSON.stringify( assertionClientExtensions )
    };
};
