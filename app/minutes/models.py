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
	topics = db.Column(db.String)
	date = db.Column(db.DateTime)
	body = db.Column(db.String)
	committee_id = db.Column(db.String, db.ForeignKey('committee.id'))
	committee = db.relationship("Committee", back_populates="minutes")
