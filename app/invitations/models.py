"""
filename: models.py
description: Model for committee invitations.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/19/17
"""

from app import db

class Invitations(db.Model):
	__tablename__ = 'invitations'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_name = db.Column(db.String(255))
	committee = db.Column(db.ForeignKey('committees.id'))
	isInvite = db.Column(db.Boolean)
