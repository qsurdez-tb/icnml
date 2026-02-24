FROM cr.unil.ch/icnml/base:latest
LABEL maintainer "Marco De Donno <Marco.DeDonno@unil.ch>"

################################################################################
#    Installation of Python and other tooling

RUN apt-get update && \
    apt-get install -y curl git python2 python2-dev libzbar-dev poppler-utils libtiff5 libtiff5-dev gnupg2 && \
    rm -rf /var/lib/apt/lists/*

COPY ./get-pip.py /tmp/get-pip.py
RUN python2 /tmp/get-pip.py

################################################################################
#    User configuration

RUN sed -i -r "/^(www-data)/!d" /etc/group /etc/passwd && \
    sed -i -r 's#^(.*):[^:]*$#\1:/sbin/nologin#' /etc/passwd

################################################################################
#    Installation of Marco De Donno's libraries and depencencies

COPY ./library /var/www/library
RUN find /var/www/library -name 'requirements.txt' -exec pip install --no-cache-dir -r {} \;
RUN find /var/www/library -maxdepth 1 -mindepth 1 > /usr/local/lib/python2.7/dist-packages/mdedonno.pth

RUN chmod +x /var/www/library/WSQ/WSQ/NBIS/cwsq && \
    chmod +x /var/www/library/WSQ/WSQ/NBIS/dwsq

WORKDIR /var/www/library/NIST
RUN python2 doctester.py

WORKDIR /var/www/library/MDmisc
RUN python2 doctester.py

################################################################################
#    Copy the font to the system

COPY arial.ttf /usr/share/fonts/arial.ttf

################################################################################
#    Add the web module

COPY ./app/requirements.txt /var/www/html/requirements.txt
RUN pip install --no-cache-dir -r /var/www/html/requirements.txt

COPY ./keys /keys

COPY ./app /var/www/html
RUN find /var/www/html -name '*.py' -exec python2 -m py_compile {} \;

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /var/www/html
ENTRYPOINT /entrypoint.sh

RUN chown -R www-data:www-data /var/www/library
RUN chown -R www-data:www-data /var/www/html

USER www-data

################################################################################
#    Use by default a self-signed certificate

ENV ICNML_SSL=1

