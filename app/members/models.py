"""
filename: members.py
description: Model for Members in Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""

from app import db
from enum import Enum
from sqlalchemy_utils import ChoiceType
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class Roles(Enum):
	NormalMember = "NormalMember"
	ActiveMember = "ActiveMember"
	MinuteTaker = "MinuteTaker"
	CommitteeHead = "CommitteeHead"

class Members(db.Model):
	__tablename__ = 'members'
	committees_id = db.Column(db.String(255), db.ForeignKey('committees.id'), primary_key=True)
	users_id = db.Column(db.String(255), db.ForeignKey('users.id'), primary_key=True)
	role = db.Column(ChoiceType(Roles, impl=db.String()))
	member = db.relationship('Users', backref= db.backref('committees', lazy='dynamic'))
	committee = db.relationship('Committees', backref= db.backref('members', lazy='dynamic'))
