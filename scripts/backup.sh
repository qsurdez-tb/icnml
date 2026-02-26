#!/bin/bash

DBUSER=icnml
DBNAME=icnml
HOST=icnml.local

DIRNAME=/mnt/backup

DEKTABLE=donor_dek
CFTABLE=cf

CURRENT_DATE=$(date "+%Y-%m-%d-%H%M%S")
FILENAME_START=${DBNAME}_${CURRENT_DATE}
FILENAME_DATA=${FILENAME_START}_data.backup
FILENAME_DEK=${FILENAME_START}_dek.backup
FILENAME_CF=${FILENAME_START}_cf.backup

PASS=$(openssl rand -base64 32 | sha256sum | cut -d' ' -f1)

USERS=("mdedonno1337@gmail.com" "marco.dedonno@unil.ch" "christophe.champod@unil.ch" "heidi.eldridge@icloud.com" "icnml@unil.ch")
NBUSERS=${#USERS[@]}
THRESHOLD=2

SHARES=$(echo ${PASS} | ssss-split -t ${THRESHOLD} -n ${NBUSERS} -Q)
i=0
for s in ${SHARES}
do
    cat <<EOF | gpg --encrypt --armor --recipient ${USERS[$i]} > ${DIRNAME}/${FILENAME_START}_ssss_${USERS[$i]}.asc
This will allow the ICNML admin to decrypt the backup for the: ${CURRENT_DATE}.
At least ${THRESHOLD} out of ${NBUSERS} has to be meet to be able to unencrypt the backup.

If you agree the access to this backup, send this code back to the admin:
    
ssss_key: ${s}
    
EOF
    
    i=$i+1
done

pg_dump -v -h ${HOST} -U ${DBUSER} -T ${DEKTABLE} -T ${CFTABLE} -Fc ${DBNAME} | gpg --armor --symmetric --cipher-algo AES256 --batch --yes --passphrase ${PASS} > ${DIRNAME}/${FILENAME_DATA}
pg_dump -v -h ${HOST} -U ${DBUSER} -t ${DEKTABLE}               -Fc ${DBNAME} | gpg --armor --symmetric --cipher-algo AES256 --batch --yes --passphrase ${PASS} > ${DIRNAME}/${FILENAME_DEK}
pg_dump -v -h ${HOST} -U ${DBUSER}                -t ${CFTABLE} -Fc ${DBNAME} | gpg --armor --symmetric --cipher-algo AES256 --batch --yes --passphrase ${PASS} > ${DIRNAME}/${FILENAME_CF}

PASS=$(openssl rand -base64 32)

