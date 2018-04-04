"""
filename: test_committees.py
description: Tests for Committees.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 03/21/18
"""

import pytest
import config
from app import app, db, socketio
from app.charges.charges_response import Response
from app.committees.models import Committees
from app.users.permissions import Permissions
from app.charges.models import *
from app.users.models import Users
from flask_socketio import SocketIOTestClient
from flask_sqlalchemy import SQLAlchemy

class TestCharges(object):

    @classmethod
    def setup_class(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_TEST_DATABASE_URI
        db = SQLAlchemy(app)
        db.session.close()
        db.drop_all()
        db.create_all()
        self.socketio = socketio.test_client(app);
        self.socketio.connect()

    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        self.socketio.disconnect()

    @classmethod
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

        # Create a test committee.
        committee = Committees(id = "testcommittee")
        committee.title = "Test Committee"
        committee.description = "Test Description"
        committee.location = "Test Location"
        committee.meeting_time = "1300"
        committee.meeting_day =  2
        committee.head = "adminuser"
        self.committee = committee
        db.session.add(committee)
        db.session.commit()

        self.charge_dict={
            'id': 10,
            'title': 'Test Charge',
            'description': 'Test Description',
            'committee': 'Commitee title',
            'committee_id': 'ID',
            'priority': PriorityType.Low
        }

        # Create a test charge.
        charge = Charges(id = 10)
        charge.author = "testuser"
        charge.title = "Test Charge"
        charge.description = "Test Description"
        charge.committee = "testcommittee"
        charge.priority = PriorityType.Low
        charge.status = StatusType.Unapproved
        self.charge = charge

        db.session.add(charge)
        db.session.commit()


    # Test when an admin creates a committee.
    def test_admin_create_charge(self):
        user_data = {
            "token": self.admin_token,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    # Test when a charge is created with no committee
    def test_create_charge_no_committee(self):
        user_data = {
            "token": self.admin_token,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": ""
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrChargeDontExist

    # Test when a charge is created with no title
    def test_create_charge_invalid_title(self):
        user_data = {
            "token": self.admin_token,
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InvalidTitle

    # Test when a charge is created with an invalid priority
    def test_create_charge_invalid_priority(self):
        user_data = {
            "token": self.admin_token,
            "title": "test charge",
            "priority": 999,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InvalidPriority

    # Test getting a charge
    def test_get_charge(self):

        self.socketio.emit('get_charge', 10)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == self.charge_dict

    # Test getting a charge that doesn't exist
    def test_get_charge_doesnt_exist(self):

        self.socketio.emit('get_charge', 99999)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrChargeDontExist

        # Test getting a charge
    def test_get_charges(self):
        response_data = [{
            'id': 10,
            'title': 'Test Charge',
            'description': 'Test Description'
        }]

        self.socketio.emit('get_charges', "testcommittee")
        received = self.socketio.get_received()
        assert received[0]["args"][0] == response_data

    # Test getting a charge that doesn't exist
    def test_get_charges_doesnt_exist(self):

        self.socketio.emit('get_charges', "test")
        received = self.socketio.get_received()
        assert received[0]["args"][0] == []

    def test_edit_charge(self):

        user_data = {
            "token": self.admin_token,
            "charge": 10,
            "title": "this is the new title"
        }
        self.charge_dict["title"] = user_data["title"]

        self.socketio.emit('edit_charge', user_data)
        received = self.socketio.get_received()
        print(received)
        assert received[1]["args"][0] == self.charge_dict


    def test_edit_charge_not_authorized(self):

        user_data = {
            "token": self.user_token,
            "charge": 10,
            "title": "this is the new title"
        }
        self.charge_dict["title"] = user_data["title"]

        self.socketio.emit('edit_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditError
