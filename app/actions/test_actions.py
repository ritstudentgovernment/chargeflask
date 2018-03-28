"""
filename: test_actions.py
description: Tests for Actions.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 03/23/18
"""

import pytest
import config
from app import app, db, socketio
from app.actions.actions_response import Response
from app.actions.models import *
from app.committees.models import *
from app.charges.models import *
from app.users.permissions import Permissions
from app.users.models import Users
from flask_socketio import SocketIOTestClient
from flask_sqlalchemy import SQLAlchemy
import base64


class TestAction(object):

    @classmethod
    def setup_class(self):
        self.app = app.test_client()

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE'] = config.SQLALCHEMY_TEST_DATABASE_URI
        db = SQLAlchemy(app)
        db.session.close()
        db.drop_all()
        db.create_all()
        self.socketio = socketio.test_client(app);
        self.socketio.connect()

    def setup_method(self, method):
        db.drop_all()
        db.create_all()

        # Create admin user for tests.
        admin = Users(id = "adminuser")
        admin.first_name = "Admin"
        admin.last_name = "User"
        admin.email = "adminuser@test.com"
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
        self.test_admin = admin
        self.admin_token = admin.generate_auth()
        self.admin_token = self.admin_token.decode('ascii')

        # Create normal user for tests.
        user = Users(id = "testuser")
        user.first_name = "Test1"
        user.last_name = "User"
        user.email = "testuser@test.com"
        user.is_admin = False
        db.session.add(user)
        db.session.commit()
        self.test_user = user
        self.user_token = user.generate_auth()
        self.user_token = self.user_token.decode('ascii')

        self.test_committee_dict = {
            "id" : "testcommittee",
            "title": "testcommittee",
            "description": "Test Description",
            "location": "Test Location",
            "meeting_time": "1300",
            "meeting_day": 2,
            "head": "testuser",
            "committee_img": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        }
        self.test_committee = Committees(id = "testcommittee")
        self.test_committee.title = self.test_committee_dict["title"]
        self.test_committee.location = self.test_committee_dict["location"]
        self.test_committee.description = self.test_committee_dict["description"]
        self.test_committee.meeting_time = self.test_committee_dict["meeting_time"]
        self.test_committee.meeting_day = self.test_committee_dict["meeting_day"]
        self.test_committee.head = self.test_committee_dict["head"]
        com_img = base64.b64decode(self.test_committee_dict["committee_img"])
        self.test_committee.com_image = com_img

        db.session.add(self.test_committee)
        db.session.commit()

        # Create a test charge.
        charge = Charges(id = 10)
        charge.author = "testuser"
        charge.title = "Test Charge"
        charge.description = "Test Description"
        charge.committee = "testcommittee"
        charge.priority = ChargePriorityType.Low
        charge.status = ChargeStatusType.Unapproved
        self.test_charge = charge
        db.session.add(self.test_charge)
        db.session.commit()

        # Create a test action.
        action = Actions(id = 10)
        action.author = self.test_admin.id
        action.title = "Test Action"
        action.description = "Test Description"
        action.charge = 10
        action.status = ActionStatusType.InProgress
        self.test_action = action
        db.session.add(self.test_action)
        db.session.commit()

    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        self.socketio.disconnect()

    # Test creating an action
    def test_create_action(self):
        user_data = {
            "token": self.admin_token,
            "charge": 10,
            "assigned_to": "testuser",
            "title": "test title",
            "description": "test description"
        }

        self.socketio.emit('create_action', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    # Test creating an action with no description
    def test_create_action_no_description(self):
        user_data = {
            "token": self.admin_token,
            "charge": 10,
            "assigned_to": "testuser",
            "title": "test title",
        }

        self.socketio.emit('create_action', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddError

    # Test creating an action while not authorized to do so
    def test_create_action_not_authorized(self):
        user_data = {
            "token": self.user_token,
            "charge": 10,
            "assigned_to": "testuser",
            "title": "test title",
            "description": "test description"
        }

        self.socketio.emit('create_action', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrNotAuth

    # Test creating an action without a valid charge
    def test_create_action_no_charge(self):
        user_data = {
            "token": self.user_token,
            "charge": 9999,
            "assigned_to": "testuser",
            "title": "test title",
            "description": "test description"
        }

        self.socketio.emit('create_action', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrChargeDontExist
