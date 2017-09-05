"""
filename: users.py
description: Model for profiles.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""
from app import db

class Users(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True, unique= True)
	first_name = db.Column(db.String(255))
	last_name = db.Column(db.String(255))
	email = db.Column(db.String(255))