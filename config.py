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

#Define the database URI (Postgres)
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgres://localhost/tigertracker')
SQLALCHEMY_TEST_DATABASE_URI = os.environ.get('SQLALCHEMY_TEST_DATABASE_URI', 'postgres://localhost/tigertrackertest')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for signing tokens
SECRET_KEY = os.environ.get('APP_SECRET_KEY', '')

# Email configuration
MAIL_SERVER = os.environ.get('MAIL_HOST', 'mymail.rit.edu')
MAIL_PORT = 465
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

# WebClient URL (For email support, client: https://git.io/vFDqH)
# Shoud follow the pattern https://<client-url>/invitation/
CLIENT_URL = os.environ.get('CLIENT_URL', 'http://localhost:3000/invitation/')
