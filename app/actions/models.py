"""
filename: models.py
description: Model for Charge Actions.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/05/17
"""

from app import db
from sqlalchemy_utils import ChoiceType

class Actions(db.Model):
	__tablename__ = 'actions'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	title = db.Column(db.String(255))
	description = db.Column(db.String)
	assigned_to = db.Column(db.ForeignKey('users.id'))
	charge = db.Column(db.ForeignKey('charges.id'))
	notes = db.relationship('Notes', backref='actions', lazy='dynamic')
	created_at = db.Column(db.DateTime, server_default= db.func.now())
	
	
	status_types = [(0, "In Progress"), (1, "Indefinite"), (2, "Unknown"),
					(3, "Completed"), (4, "Stopped"), (5, "Incomplete"), (6, "On Hold")]

	action_status = db.Column(ChoiceType(status_types))
