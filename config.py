"""
filename: config.py
description: Configuration file for Charge Tracker app.
author: Omar De La Hoz (oed7416@rit.edu)
created on: 09/05/17
"""
import os

DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#Define the databae URI (Postgres)
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/chargetracker'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for signing tokens
SECRET_KEY = "secret"