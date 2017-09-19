"""
filename: controllers.py
description: Controller for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/19/17
"""

from flask_socketio import emit
from app import socketio, db
from app.committees.models import Committees
from app.users.models import Users

@socketio.on('get_committees')
def get_committees():
	committees = Committees.query.all()
	comm_ser = [{"id": c.id, "title": c.title, "description": c.description} for c in committees]
	emit("get_committees", {"committees": comm_ser, "count": len(committees)})


@socketio.on('get_committee')
def get_committee(committee_id):

	committee = Committees.query.filter_by(id = committee_id).first()

	if committee is not None:

		emit("get_committee", {"id": committee.id, "title": committee.title, 
								"description": committee.description})
	else:
		emit("error", "Committee doesn't exist.")





