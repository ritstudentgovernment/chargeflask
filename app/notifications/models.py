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

##
## @brief      Class for notification type.
##
class NotificationType(Enum):
    MentionedInNote  = "MentionedInNote"
    AssignedToAction = "AssignedToAction"
    MadeCommitteeHead = "MadeCommitteeHead"
    UserRequest = "UserRequest"


##
## @brief      Class for notifications.
##
class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.ForeignKey('users.id'))
    type = db.Column(ChoiceType(NotificationType, impl = db.String()))
    destination = db.Column(db.String)
    message = db.Column(db.String)
    redirect = db.Column(db.String)
