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
from flask_socketio import SocketIO
from raven.contrib.flask import Sentry

# Create the app and add configuration.
app = Flask(__name__, template_folder='static')
app.config.from_object('config')
sentry = Sentry(app)
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Import each module created.
from app.users.controllers import *
from app.committees.controllers import *
from app.members.controllers import *
from app.charges.controllers import *
from app.actions.controllers import *
from app.committee_notes.controllers import *
from app.notes.controllers import *
from app.actions.models import Actions
from app.notes.models import Notes
db.create_all()
