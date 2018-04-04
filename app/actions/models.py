"""
filename: models.py
description: Model for Charge Actions.
created by: Omar De La Hoz (oed7416@rit.edu)
Chris Lemelin (cxl8826@rit.edu)
created on: 09/05/17
"""

from app import db
from sqlalchemy_utils import ChoiceType
from enum import Enum

##
## @brief      Status types for Actions.
##
class ActionStatusType(Enum):
	InProgress	= 0
	Indefinite	= 1
	Unknown	= 2
	Completed	= 3
	Stopped	= 4
	Incompleted	= 5
	OnHold	= 6

class Actions(db.Model):
	__tablename__ = 'actions'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	title = db.Column(db.String(255))
	description = db.Column(db.String)
	assigned_to = db.Column(db.ForeignKey('users.id'))
	charge = db.Column(db.ForeignKey('charges.id'))
	notes = db.relationship('Notes', backref='actions', lazy='dynamic')
	created_at = db.Column(db.DateTime, server_default= db.func.now())
	status = db.Column(db.Enum(ActionStatusType))
