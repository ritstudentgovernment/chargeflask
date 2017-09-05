"""
filename: users.py
description: Model for Users.
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

	# Generate an API token for user authentication.
	def generate_auth(self, expiration):
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
		user = User.query.get(data['id'])
		return user