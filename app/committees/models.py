"""
filename: committees.py
description: Model for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""
from app import db

class Committees(db.Model):
	__tablename__ = 'committees'
	id = db.Column(db.String(255), primary_key=True, unique= True)
	title = db.Column(db.String(255))
	description = db.Column(db.String(255))
	head = db.Column(db.ForeignKey('users.id'))
	location = db.Column(db.String(255))
	meeting_day = db.Column(db.Integer)
	meeting_time = db.Column(db.Time)
	members = db.relationship('Members', backref='committees', lazy='dynamic')