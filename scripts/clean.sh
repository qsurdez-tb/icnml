#!/bin/bash

DIRNAME=/mnt/escnas/backup/

find ${DIRNAME} -type f -mtime +30 -exec rm -f {} \;

