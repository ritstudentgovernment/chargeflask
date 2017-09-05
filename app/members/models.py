"""
filename: members.py
description: Model for Members in Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""

from .. import *
from sqlalchemy_utils import ChoiceType
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class Members(db.Model):
	__tablename__ = 'members'
	id = db.Column(db.Integer, primary_key=True, unique= True)
	committee = db.Column(db.ForeignKey('committees.id'))
	member = db.Column(db.ForeignKey('users.id'))
	member_types = [(0, "Head"), (1, "Member")]
	member_type = db.Column(ChoiceType(member_types))

	def generate_auth(self, expiration):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({ 'id': self.id })

