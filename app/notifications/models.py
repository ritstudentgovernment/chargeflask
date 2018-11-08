"""
filename: models.py
description: Models for notifications
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 11/08/18
"""

from app import db
from app.users.models import Users
from sqlalchemy.dialects.postgresql import *
from sqlalchemy_utils import ChoiceType
from enum import Enum

class NotificationType(Enum)
    MentionedInNote  = 0
    AssignedToTask = 1
    MadeCommitteeHead = 2


class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.ForeignKey('users.id'))
    notification_type = db.Column(ChoiceType(NotificationType, impl = db.Integer()))
    destination = db.Column(db.String)
    