"""
filename: controllers.py
description: Cronrollers for Minutes.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 02/12/19
"""

from flask_socketio import emit
from app.decorators import ensure_dict, get_user
from app import socketio, db
from app.charges.models import *
from app.committees.models import Committees
from app.minutes.models import Minutes, Topics
from app.users.models import Users

@socketio.on('create_minute')
@ensure_dict
@get_user
def create_minute(user_data):
    committee =  Committees.query.filter_by(id = user_data.get("committee","")).first()

    if (committee is None or user_data["title"] is None
        or user_data[""]