"""
filename: charges.py
description: Model for charges.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/30/17
"""

from app import db

class Charges(db.Model):
	__tablename__ = 'charges'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	title = db.Column(db.String(255))
	author = db.Column(db.ForeignKey('users.id'))
	description = db.Column(db.String(255))
	created_at = db.Column(db.DateTime, server_default= db.func.now())
	committee = db.Column(db.ForeignKey('committees.id'))
	objectives = db.Column(ARRAY(db.String))
	schedule = db.Column(ARRAY(db.String))
	actions = db.relationship('Actions', backref='charges', lazy='dynamic')
	resources = db.Column(ARRAY(db.String))
	stakeholders = db.Column(ARRAY(db.String))

	priority_types = [(0, "Low"),(1, "Medium"), (2, "High")]
	priority = db.Column(ChoiceType(priority_types))

	status_types = [(0, "Unapproved"),  (1, "Failed"),  (2, "In Progress"), 
					(3, "Indefinite"),  (4, "Unknown"), (5, "Completed"),
					(6, "Not Started"), (7, "Stoppped")]

	status = db.Column(ChoiceType(status_types))
	