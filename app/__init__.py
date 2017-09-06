"""
filename: __init__.py
description: Initiate Charge Tracker app
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/07/17
"""

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import *
from sqlalchemy_utils import ChoiceType

# Create the app and add configuration.
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# Import each module created.
from app.users.models import Users
from app.charges.models import Charges
from app.committees.models import Committees
from app.members.models import Members
from app.actions.models import Actions
from app.notes.models import Notes
db.create_all()