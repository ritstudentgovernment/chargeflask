"""
filename: check_data_type.py
description: Checks if incoming data is a dictionary.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/13/18
"""
import functools
from flask_socketio import emit, disconnect
from app.users.models import Users
from flask_login import current_user
from flask import request

def ensure_dict(types):
    @functools.wraps(types)
    def wrapped(*args, **kwargs):
        if type(args[0]) is dict:
            return types(*args, **kwargs)
        else:
            emit(request.event["message"], {"error": "Please check data type."})
    return wrapped


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):

        user = None

        if (args[0].get("token", "") != "" and 
            args[0].get("token", "") != None):
            user = Users.verify_auth(args[0].get("token",""))
        elif current_user.is_authenticated:
            user = current_user

        return f(user, *args, **kwargs)
    return wrapped