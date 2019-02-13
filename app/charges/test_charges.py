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
from app.members.models import Members, Roles
from app.users.models import Users
from flask_socketio import SocketIOTestClient
from app.notifications.controllers import new_committee
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
        db.event.remove(Committees, "after_insert", new_committee)
        self.socketio = socketio.test_client(app);
        self.socketio.connect()

    @classmethod
    def teardown_class(self):
        db.event.listen(Committees, "after_insert", new_committee)
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

        # Create normal user for tests.
        user2 = Users(id = "testuser2")
        user2.first_name = "Test"
        user2.last_name = "User"
        user2.email = "testuser@test.com"
        user2.is_admin = False
        db.session.add(user2)
        db.session.commit()
        self.test_user2 = user2
        self.user_token2 = user2.generate_auth()
        self.user_token2 = self.user_token2.decode('ascii')

        # Create normal user for tests.
        user3 = Users(id = "activemember")
        user3.first_name = "Active"
        user3.last_name = "Member"
        user3.email = "testuser@test.com"
        user3.is_admin = False
        db.session.add(user2)
        db.session.commit()
        self.test_user3 = user3
        self.user_token3 = user3.generate_auth()
        self.user_token3 = self.user_token3.decode('ascii')


        # Create a test committee.
        committee = Committees(id = "testcommittee")
        committee.title = "Test Committee"
        committee.description = "Test Description"
        committee.location = "Test Location"
        committee.meeting_time = "1300"
        committee.meeting_day =  2
        committee.head = "testuser"
        self.committee = committee

        # Add user3 to committee.
        role = Members(role= Roles.ActiveMember)
        role.member = self.test_user3
        self.committee.members.append(role)
        db.session.add(self.committee)
        db.session.commit()

        self.charge_dict={
            'id': 10,
            'title': 'Test Charge',
            'description': 'Test Description',
            'committee': 'testcommittee',
            'status': 0,
            'priority': 0,
            'private': True,
            'paw_links': "https://testlink.com"
        }

        # Create a test charge.
        charge = Charges(id = 10)
        charge.author = "testuser"
        charge.title = "Test Charge"
        charge.description = "Test Description"
        charge.committee = "testcommittee"
        charge.paw_links = "https://testlink.com"
        charge.priority = 0
        charge.status = 0
        charge.private  = True
        self.charge = charge

        db.session.add(charge)
        db.session.commit()
        self.charge_dict["created_at"] = self.charge.created_at.isoformat()


    # Test when an admin creates a committee.
    def test_admin_create_charge(self):
        user_data = {
            "token": self.admin_token,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee",
            "private": False
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    def test_head_create_charge(self):
        user_data = {
            "token": self.user_token,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    def test_active_member_create_charge(self):
        user_data = {
            "token": self.user_token3,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    def test_create_charge_no_permission(self):
        user_data = {
            "token": self.user_token2,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.PermError


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

    # Test when a charge is created with no priority
    def test_create_charge_no_priority(self):
        user_data = {
            "token": self.admin_token,
            "title": "test charge",
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InvalidPriority

    def test_create_charge_priority_invalid_type(self):
        user_data = {
            "token": self.admin_token,
            "title": "test charge",
            "priority": None,
            "description": "test description",
            "committee": "testcommittee"
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InvalidPriority

    def test_active_member_create_charge_public(self):
        user_data = {
            "token": self.user_token3,
            "title": "test charge",
            "priority": 0,
            "description": "test description",
            "committee": "testcommittee",
            "private": False
        }

        self.socketio.emit('create_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.PermError

    # Test getting a charge being a member.
    def test_get_charge(self):

        user_data = {
            "token": self.user_token3,
            "charge": 10
        }

        self.socketio.emit('get_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == self.charge_dict

    # Test getting a charge being an admin.
    def test_get_charge(self):

        user_data = {
            "token": self.admin_token,
            "charge": 10
        }

        self.socketio.emit('get_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == self.charge_dict

    # Test getting charge no permissions.
    def test_get_charge_noperm(self):

        user_data = {
            "token": self.user_token2,
            "charge": 10
        }

        self.socketio.emit('get_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.PermError

    # Test getting a charge that doesn't exist
    def test_get_charge_doesnt_exist(self):

        user_data = {
            "token": self.user_token,
            "charge": 99999
        }

        self.socketio.emit('get_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrChargeDontExist

    # Test getting a charge
    def test_get_charges(self):
        response_data = [ self.charge_dict ]

        user_data = {
            "token": self.user_token3,
            "committee_id": "testcommittee",
        }

        self.socketio.emit('get_charges', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == response_data

    # Test getting a charge not member
    def test_get_charges_not_member(self):

        user_data = {
            "token": self.user_token2,
            "committee_id": "testcommittee",
        }

        self.socketio.emit('get_charges', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == []

    # Test getting a charge that doesn't exist
    def test_get_charges_doesnt_exist(self):

        user_data = {
            "token": self.user_token3,
            "committee_id": "test",
        }

        self.socketio.emit('get_charges', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == []

    # Get all public charges.
    def test_get_all_charges(self):
        self.socketio.emit('get_all_charges')
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
        assert received[1]["args"][0] == self.charge_dict

    def test_edit_charge_no_id(self):

        user_data = {
            "token": self.admin_token,
            "title": "this is the new title"
        }
        self.charge_dict["title"] = user_data["title"]

        self.socketio.emit('edit_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrChargeDontExist


    def test_edit_charge_not_authorized(self):

        user_data = {
            "token": self.user_token2,
            "charge": 10,
            "title": "this is the new title"
        }
        self.charge_dict["title"] = user_data["title"]

        self.socketio.emit('edit_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.PermError

    def test_edit_charge_active_member_public(self):

        user_data = {
            "token": self.user_token3,
            "charge": 10,
            "title": "this is the new title",
            "private": False
        }
        self.charge_dict["title"] = user_data["title"]

        self.socketio.emit('edit_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.PermError

    def test_edit_charge_active_member_public_notbool(self):

        user_data = {
            "token": self.user_token3,
            "charge": 10,
            "title": "this is the new title",
            "private": "False"
        }
        self.charge_dict["title"] = user_data["title"]

        self.socketio.emit('edit_charge', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditError
