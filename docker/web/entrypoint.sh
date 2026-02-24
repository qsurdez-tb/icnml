#!/bin/bash

openssl req -subj '/CN=icnml.local/' -newkey rsa:2048 -new -nodes -x509 -days 365 -keyout /tmp/key.pem -out /tmp/cert.pem > /dev/null 2>&1

python2 /var/www/html/runner.py
