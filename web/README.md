# ICNML web application

This repository contains the web app at the core of the platform.

It contains the python code to run the web interface, file processing and external libs serving (CDN).
The other libs mandatory for this application to run (NIST, MDmisc, PMlib, PiAnoS and WSQ) are located in the docker repository (https://esc-md-git.unil.ch/ICNML/docker).

This repository cannot (and is not intended) to be run as-is since the mandatory libraries are not located here.
For development, install those libraries separately in your dev environment.

# Encryption keys and Hashing functions

All the data that is "encrypted" is encrypted with AES256. The passed in parameters is hashed with a SHA256 function to uniformize the encryption key ("key"). The initialization vector is always set to a random value (with the Crypto library), every time a value is encrypted. The encryption function as noted as follows:

    AES( data, key )

The hashing process is done with a key derivation function, in particular PBKDF2 with a SHA512 hashing function. The data and the salt are described as needed. The function is as follows:

    PBKDF2( data, salt, iterations )

If the number of iterations is not indicated, the default value is 20'000.

# Login

## Password

The login process is done in multiple steps. First, the password is hashed as follows on the cilent side (HPWCS - Hashed Password Client Side):

    HPWCS = PBDKF2( password, "icnml_" + username, 20'000 )

This hash is done not to transmit the user password in clear to the server (avoiding a memory dump or any stealing of the password). This hasing is done on the client-side, 20'000 iterations for performance issues.

This hashed password is hashed a second time on the server side as follows (HPWCSSS):

    HPWCSSS = PBDKF2( HPWCS, random_data( 65 ), 50'000 )

This hash is one with some random data as salt, and with more iterations (more performances possible on the server). This second step is done because the user input can never be trusted (computer basic rule) and to be able to change the security of the stored hashed (the number of iterations can be changed as needed on the client side without impacting the performance on the client-side.

This final hash is stored in the database and used to login the users.

## Second factor

One second factor is mandatory for all accounts. For non-admin account, a Time Based One Time Password (TOTP) is sufficient. For the admin accounts, a physical security key (yubikey) is mandatory.

# Data Encryption Workflow

The general idea is to provide security without impacting the usability or the workflow of the user. All encryption is done completely transparently to the user. All the data is protected by different solutions, according to the type of data and usage.

## Client-Side Key

While logging-in, a secondary key is derived from the password as follows:

    CSK = PBDKF2( password, "icnml_" + username + "_localpassword", 50'000 )

This key never leave the browser of the user. This key is used as encryption key for the client-side encrypted data. This key is stored in the browser with a session encryption key manadged by the server.

## Data Encryption Key (DEK)

When a new donor is created, a Data Encryption Key (DEK) is created to encrypt all images.
The donor email address is hashed as follows:

    email_hash = PBDKF2( email, "icnml_user_DEK", 20'000 )

The DEK is then generated as follows:

    DEK = PBDKF2( username + ":" + email_hash, random_data( 100 ), 500'000 )

This key is used as AES encryption key for all the images. The derivation of this key is done based upon the username and the email address of the donor. That information is only known by the submitter and the donor for the email and only by the donor and the server for the donor username. This key cannot be reconstructed only by the server operator. The key can be reconstructed by the donor+server or by the submitter+server.

To delete his information, the donor will only delete the DEK, hence removing any possibility to get the images from the live database AND ALL the backups. The submitter will have the possibility to see the images but is not a problem because his has access to the original images anyway. This feature is done to protect the privacy of the donor : the submitter cannot know if the data of the donor is still available or not because he will see his submission as usual, even if the data is not decryptable for the users.

The database table containing the DEKs is not part of the usual backups, but treated separately.

If the donor want to be removed from ICNML, the DEK will be deleted from the live database, hence removing all the possibility of decryption of the biometric data.

For privacy purpose, the submitter has access to the uploaded data even if the DEK is removed, to ensure that he will not know if the donor has removed himself from ICNML or not. This is done based upon the fact that the submitter knowns the email of the donor, and has access to the original images. The DEK is reconstructed on the fly for the particular session, only stored in the session of the submitter; meanwhile, the images are still not usable by anyone but the submitter.

The DEK can be reconstructed by the donor on his profile page. 

## Submission

### Nickname

The "nickname" is a field used by the submitter to identify the donor. This field is encrypted on the client-side with AES with the CSK as encryption key.

### Donor email

The "donor email" address is encrypted with AES (CSK key) on the client side (to be able to show it to the submitter while updating the upload data).

On the creation of the upload process, the email is sent to the server in clear (to be able to send the email to the donor), and hashed directly on the server side (PBKDF2 with 100 characters of random data and 50'000 iterations of SHA512).

### Files names

The names of the files uploaded by the submitter are encrypted on the client-side using AES with the CSK key. The filenames are important for the submitter to recognize the files already uploaded, but could contain some personal information regarding the laboratory, donor, ..., hence are encrypted.

### Images

All images are encrypted with AES using the DEK of the donor as password.

# Removal from ICNML by the donor

The donor can remove himself from ICNML without asking anyone to do it, with immediat effects. This removal is done by removing the DEK from the database, hence removing the possibility of decryption of the data. This impossibility of decryption extends immediatly to all backups of the data.

By only removing the DEK, the submitter can not know if this donor is still present or not in the database (see the DEK paragraph for more details about the temporary session DEK).

When the donor has deleted the DEK from the database, the submitter can still continue to upload some data, as usual : this data, encrypted with the temporary-DEK, will not be decryptable by anyone.

The donor can also remove completly the possibility of decryption by removing his salt. By removing the salt, the DEK can not be reconstructed, even temporary by the submitter.

# Manual creation of an admin account

There is currently no way to create in the ICNML interface an admin account, but it can be created manually an entry in the SQL database (using DWeaver for example).

## Using the password-reset procedure

This procedure is recomanded if the server has email-capabilities, and for the production server.

This will be done in the database by:

1. setting a random password for a particular email
2. asking this new admin user to go to https://icnml.unil.ch/login?/ and proceed to "password reset"
3. do the TOTP reset procedure.
4. log on to ICNML (then in ICNML a security key can be configured if desireed)

Before creating this admin account in the database we need to obtain the hash for the corresponding e-mail. It is done as follows in a docker version of ICNML to have all the required functions in a virtual python environment.

You can run it directly in docker with:

``` bash
docker run -it --entrypoint=python2 cr.unil.ch/icnml/docker/web
```

Then in the container, you can type the following.
The following code allows you to create the hash of the email, called `new_email_hash`.

Note that the `import utils` command may hang up; this is a bug that is not resolved at the moment, and will prevent to have a working docker image!
In this context, you can bypass this issue by hitting `^C` and continue with import config.

``` python
>>> import utils
>>> import config
>>>
>>> email = "marco.dedonno@unil.ch"
>>> new_email_hash = utils.hash.pbkdf2( email, utils.rand.random_data( config.EMAIL_SALT_LENGTH ), config.EMAIL_NB_ITERATIONS ).hash()
>>> new_email_hash
'pbkdf2$sha512$33SPNIJPADV9C0U640D6$50000$aed51b97378f63787f1df8320e5330a28d7f2e01ed76e247501599eaf721b173c4d23c7588c190e34ff08269f09eca193cd44f4614d41a34404ebb6eee75932c'
>>>
>>> utils.hash.pbkdf2( email, new_email_hash ).verify()
True
```

This hash shall be inserted in the database, for the correct username.

In DBeaver:
- open `ICNML>Schemas>public>users`
- right click > View Data
- add a new row with the bottom button "add new row"
- enter the email and hash (without the two quotes)
- Don't fill the `totp` nor `password` fields, those will be populated by the password reset above procedures
- check that active check box is ticked
- the type (last column) should be 1 (for admin rights; get the list of `id`s in the `account_type` table)
- save and commit

## For development

This procedure is only here to force-reset an account for development propose.

This will be done in the database by manually setting the password hash for a user.

In this example, we will use the `admin` acount.

First, run the docker container with the code base installed with:

``` 
docker run -it --entrypoint=python2 cr.unil.ch/icnml/docker/web
```

Note that the `import utils` command may hang up; this is a bug that is not resolved at the moment, and will prevent to have a working docker image!
In this context, you can bypass this issue by hitting `^C` and continue with import config.

Then in the container, you can type the following.

``` python
>>> import utils
>>> import config
>>>
>>> username = "admin"
>>> password = "mynewpassword"
>>> salt = utils.rand.random_data( config.EMAIL_SALT_LENGTH )
>>> salt
'7K95U1WDTAQ98ODUQH9D'
>>> password = utils.hash.pbkdf2( password, "icnml_" + username, 20000 ).hash()
>>> password
'pbkdf2$sha512$icnml_admin$20000$1a1eaac1001654f2d4e34c4f8b4c5c1863ed02d6c760b4532b2c0ae4639a4b3bb764a069eb2f5b16ef03a296e5ba01234ad98be33954db627a0c57617aa8d52f'
>>> password = utils.hash.pbkdf2( password, salt, config.PASSWORD_NB_ITERATIONS ).hash()
>>> password
'pbkdf2$sha512$7K95U1WDTAQ98ODUQH9D$50000$9e301e25a4083a3d530ef5555794b5cab04e827f21da6ebe7fbecaac2f0fe81a69411c817b07e7ef16a943c4c17f11ae135d2f760e6ff8513c8842669234c93e'
```

Note: It's important to have the double-hashing of the password.

Here, the value `pbkdf2$sha512$7K95U1WDTAQ98ODUQH9D$50000$9e301e25a4083a3d530ef5555794b5cab04e827f21da6ebe7fbecaac2f0fe81a69411c817b07e7ef16a943c4c17f11ae135d2f760e6ff8513c8842669234c93e` is the final hash of the password for the admin user, and will have to be saved in the database.

