"""
filename: config.py
description: Configuration file for Charge Tracker app.
author: Omar De La Hoz (oed7416@rit.edu)
created on: 09/05/17
"""
import os
import secrets

DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#Define the databae URI (Postgres)
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/chargetracker'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for signing tokens
SECRET_KEY = secrets.APP_SECRET_KEY

# Email configuration
MAIL_SERVER = 'mymail.ad.rit.edu'
MAIL_PORT = 465
MAIL_USERNAME = secrets.MAIL_USERNAME
MAIL_PASSWORD = secrets.MAIL_PASSWORD
MAIL_USE_TLS = True

# WebClient URL (For email support, client: https://git.io/vFDqH)
CLIENT_URL = 'http://localhost:3000/invitation/'
