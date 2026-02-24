FROM python:2

WORKDIR /icnml

COPY ./libraries ./libraries
COPY ./requirements.txt ./requirements.txt

RUN find . -name 'requirements.txt' -exec pip install -r {} \;
RUN find . -name 'requirements.txt' -exec realpath {} \; | xargs -n 1 dirname > /usr/local/lib/python2.7/site-packages/mdedonno.pth

COPY . .

