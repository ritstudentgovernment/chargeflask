FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get -y install git gcc libldap2-dev libsasl2-dev libxmlsec1-dev

RUN mkdir /chargeflask

RUN mkdir /chargeflask/certs

WORKDIR /chargeflask/certs

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj "/C=US/ST=New York/L=Rochester/O=RIT/OU=SG Services/CN=sg.rit.edu" -keyout sp.key -out sp.crt

WORKDIR /chargeflask

ADD ./requirements.txt /chargeflask/requirements.txt

RUN pip install -r requirements.txt

ADD . /chargeflask
