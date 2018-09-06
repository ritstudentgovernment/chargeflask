"""
filename: models.py
description: Models for Charge Notes.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/05/17
"""

from app import db

class Notes(db.Model):
	__tablename__ = 'notes'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	description = db.Column(db.String)
	status = db.Column(db.Integer)
	author = db.Column(db.ForeignKey('users.id'))
	action = db.Column(db.ForeignKey('actions.id'))
	created_at = db.Column(db.DateTime, server_default= db.func.now())
	hidden = db.Column(db.Boolean)
