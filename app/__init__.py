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
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Create the app and add configuration.
sentry_sdk.init(integrations=[FlaskIntegration()])
app = Flask(__name__, template_folder='static')
app.config.from_object('config')
socketio = SocketIO(app)
db = SQLAlchemy(app)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/saml/login'

# setup python-saml-flask
from saml import SamlManager, SamlRequest
saml_manager = SamlManager()
saml_manager.init_app(app)

# setup acs response handler
@saml_manager.login_from_acs
def login_from_acs(acs):
  # define login logic here depending on idp response
  # must call login_user() and redirect as necessary
  print(acs)
  pass


@app.route('/metadata/')
def metadata():
  saml = SamlRequest(request)
  return saml.generate_metadata()

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
