FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get -y install git gcc libldap2-dev libsasl2-dev libxmlsec1-dev

RUN mkdir /chargeflask

WORKDIR /chargeflask

ADD ./requirements.txt /chargeflask/requirements.txt

RUN pip install -r requirements.txt

ADD . /chargeflask
