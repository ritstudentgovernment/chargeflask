"""
filename: models.py
description: Model for Minutes.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 03/06/19
"""
from app import db

class Minutes(db.Model):
	__tablename__ = 'minutes'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String)
	date = db.Column(db.Integer) # EPOCH datetime.
	committee_id = db.Column(db.String, db.ForeignKey('committees.id'))
	committee = db.relationship("Committees", backref= db.backref('minutes', lazy='dynamic'))


class Topics(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	topic = db.Column(db.String)
	body = db.Column(db.String)
	minute_id = db.Column(db.Integer, db.ForeignKey('minutes.id'))
	minute = db.relationship("Minutes", backref= db.backref('topics', lazy='dynamic'))
