"""
filename: members.py
description: Model for Members in Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""

from app import db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

members_table = db.Table('members', db.Model.metadata,
	db.Column('committees_id', db.String(255), db.ForeignKey('committees.id')),
	db.Column('users_id', db.String(255), db.ForeignKey('users.id'))
)
