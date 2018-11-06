"""
filename: models.py
description: Model for Users.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""
from app import app, db, login_manager
from app.members.models import members_table
from flask_login import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class Users(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.String, primary_key=True, unique= True)
	first_name = db.Column(db.String(255))
	last_name = db.Column(db.String(255))
	email = db.Column(db.String(255))
	is_admin = db.Column(db.Boolean)
	committees = db.relationship('Committees', secondary= members_table, back_populates= 'members')


	@login_manager.user_loader
	def load_user(id):
		return Users.query.get(id)

	# Generate an API token for user authentication.
	def generate_auth(self, expiration = 60000000000000):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({ 'id': self.id })

	# Check if an API token belongs to a user and return user data.
	@staticmethod
	def verify_auth(token):
		s = Serializer(app.config['SECRET_KEY'])

		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		user = Users.query.get(data['id'])
		return user