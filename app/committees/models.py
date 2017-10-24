"""
filename: committees.py
description: Model for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/31/17
"""
from app import db
from app.members.models import members_table

class Committees(db.Model):
    __tablename__ = 'committees'
    id = db.Column(db.String(255), primary_key=True, unique= True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    head = db.Column(db.ForeignKey('users.id'))
    location = db.Column(db.String(255))
    committee_img = db.Column(db.LargeBinary)
    meeting_time = db.Column(db.String(4))   # In the format of "1300" for 1:00PM
    meeting_day = db.Column(db.Integer)      # Where 0-Sunday and 6-Saturday
    enabled = db.Column(db.Boolean, default= True)
    members = db.relationship('Users', secondary= members_table, back_populates="committees")