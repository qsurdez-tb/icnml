async function generateKey( word, salt, iterations, hash_name )
{
    iterations = iterations || 20000;
    
    hash_name = hash_name || "SHA-512";
    
    var encoder = new TextEncoder();
    var saltBuffer = encoder.encode( salt );
    var wordBuffer = encoder.encode( word );

    return await window.crypto.subtle.importKey(
        "raw",
        wordBuffer,
        { name: "PBKDF2"},
        false,
        [ "deriveBits", "deriveKey" ]
    )
    .then( function( key )
    {
        return window.crypto.subtle.deriveKey(
        {
            "name": "PBKDF2",
            "salt": saltBuffer,
            "iterations": iterations,
            "hash": hash_name
        },
        key,
        {
            "name": "HMAC",
            "hash": { "name": hash_name }
        },
        true,
        [ "sign" ] )
    } )
    .then( function( webKey )
    {
        return crypto.subtle.exportKey( "raw", webKey );
    } )
    .then( function( buffer )
    {
        return bytesToHexString( buffer );
    } );
}

function bytesToHexString( bytes )
{
    if( ! bytes )
        return null;
    
    bytes = new Uint8Array( bytes );
    var hexBytes = [];
    
    for( var i = 0; i < bytes.length; ++i )
    {
        var byteString = bytes[ i ].toString( 16 );
        if( byteString.length < 2 )
            byteString = "0" + byteString;
        hexBytes.push( byteString );
    }

    return hexBytes.join( "" );
}

function SVG( tag ) {
    return document.createElementNS( 'http://www.w3.org/2000/svg', tag );
}

function encrypt( data, pass )
{
    var salt = CryptoJS.lib.WordArray.random( 128/8 );
    
    var key = CryptoJS.PBKDF2( pass, salt, {
        keySize: 256/32,
        iterations: 100
    } );
    
    var iv = CryptoJS.lib.WordArray.random( 128/8 );
    
    var encrypted = CryptoJS.AES.encrypt( data, key, { 
        iv: iv, 
        padding: CryptoJS.pad.Pkcs7,
        mode: CryptoJS.mode.CBC
    } );
    
    var ret = salt.toString() + iv.toString() + encrypted.toString();
    return ret.replace( /(?:\r\n|\r|\n)/g, '' );
}

function decrypt( data, pass )
{
    var salt      = CryptoJS.enc.Hex.parse( data.substr( 0, 32 ) );
    var iv        = CryptoJS.enc.Hex.parse( data.substr( 32, 32 ) );
    var encrypted = data.substring( 64 );
    
    var key = CryptoJS.PBKDF2( pass, salt, {
        keySize: 256/32,
        iterations: 100
    } );
    
    var decrypted = CryptoJS.AES.decrypt( encrypted, key, { 
        iv: iv, 
        padding: CryptoJS.pad.Pkcs7,
        mode: CryptoJS.mode.CBC
    } )
    
    return decrypted.toString( CryptoJS.enc.Utf8 );
}

function truncate( str, n )
{
    return ( str.length > n ) ? str.substr(0, n-1) + '…' : str;
}

function mod( a, b )
{
    return ( ( a % b ) + b ) % b;
}

