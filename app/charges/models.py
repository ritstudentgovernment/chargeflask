"""
filename: charges.py
description: Model for charges.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 08/30/17
"""

from app import db
from sqlalchemy.dialects.postgresql import *
from sqlalchemy_utils import ChoiceType

##
## @brief      Charges Model.
##

from sqlalchemy.ext.mutable import Mutable

## 
## Class to create a mutable list in postgreSQL.
## This is used for the progress_notes column
##
class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    def edit(self, index, value):
        list.pop(self, index)
        list.insert(self, index, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value
        
class Charges(db.Model):
    __tablename__ = 'charges'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(255))
    author = db.Column(db.ForeignKey('users.id'))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default= db.func.now())
    committee = db.Column(db.ForeignKey('committees.id'))
    objectives = db.Column(ARRAY(db.String))
    schedule = db.Column(ARRAY(db.String))
    actions = db.relationship('Actions', backref='charges', lazy='dynamic')
    resources = db.Column(ARRAY(db.String))
    stakeholders = db.Column(ARRAY(db.String))
    paw_links = db.Column(db.String)
    priority = db.Column(db.Integer)
    status = db.Column(db.Integer)
    private = db.Column(db.Boolean)
    progress_notes = db.Column(MutableList.as_mutable(ARRAY(db.String)))