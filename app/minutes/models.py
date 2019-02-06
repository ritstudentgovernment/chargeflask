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
	topics = db.relationship("Topics")
	date = db.Column(db.DateTime)
	committee_id = db.Column(db.String, db.ForeignKey('committees.id'))
	committee = db.relationship("Committee", back_populates="minutes")


class Topics(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	topic = db.Column(db.String)
	body = db.Column(db.String)
	minute_id = db.Column(db.Integer, db.ForeignKey('minutes.id'))