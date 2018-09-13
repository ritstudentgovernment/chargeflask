"""
filename: check_data_type.py
description: Checks if incoming data is a dictionary.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/13/18
"""
import functools
from flask_socketio import emit
from flask import request

def checkDict(types):
	
    @functools.wraps(types)
    def wrapped(*args, **kwargs):
        if type(args[0]) is dict:
            return types(*args, **kwargs)
        else:
            emit(request.event["message"], {"error": "Please check data type."})
    return wrapped