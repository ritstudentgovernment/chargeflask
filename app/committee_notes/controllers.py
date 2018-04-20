"""
filename: controllers.py
description: Controllers for committee notes.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/20/18
"""

from flask_socketio import emit
from app import socketio, db
from app.committee_notes.models import *
