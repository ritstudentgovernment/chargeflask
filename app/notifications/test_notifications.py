"""
filename: test_notifications.py
description: Tests for Notifications.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 11/09/18
"""

import pytest
import config
from app import app, db, socketio
from app.users.models import Users
from app.notifications.models import Notifications, NotificationType
from app.charges.controllers import Charges
from app.committees.controllers import Committees
from app.notifications.controllers import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

class TestNotifications(object):

    @classmethod
    def setup_class(self):
        self.app = app.test_client()
        
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_TEST_DATABASE_URI
        db = SQLAlchemy(app)
        db.session.close()
        db.drop_all()
        db.create_all()


    def setup_method(self, method):
        db.drop_all()
        db.create_all()
        self.socketio = socketio.test_client(app);
        self.socketio.connect()

        db.event.remove(Committees, "after_insert", new_committee)
        db.event.remove(Actions, "after_insert", new_action)

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
        user_two = Users(id = "testuser2")
        user_two.first_name = "Test2"
        user_two.last_name = "User"
        user_two.email = "testuser@test.com"
        user_two.is_admin = False
        db.session.add(user_two)
        db.session.commit()
        self.test_user_two = user_two
        self.user_token_two = user_two.generate_auth()
        self.user_token_two = self.user_token_two.decode('ascii')

        # Create a test committee.
        committee = Committees(id = "testcommittee")
        committee.title = "Test Committee"
        committee.description = "Test Description"
        committee.location = "Test Location"
        committee.meeting_time = "1300"
        committee.meeting_day =  2
        committee.head = "testuser"
        self.committee = committee
        db.session.add(committee)
        db.session.commit()

        # Create a test charge.
        charge = Charges(id = 10)
        charge.author = "testuser"
        charge.title = "Test Charge"
        charge.description = "Test Description"
        charge.committee = "testcommittee"
        charge.paw_links = "https://testlink.com"
        charge.priority = 0
        charge.status = 0
        self.charge = charge
        db.session.add(charge)
        db.session.commit()

        # Create a test action.
        action = Actions(id = 10)
        action.author = admin.id
        action.title = "Test Action"
        action.description = "Test Description"
        action.charge = 10
        action.status = 0
        self.test_action = action
        db.session.add(self.test_action)
        db.session.commit()

        db.event.listen(Committees, "after_insert", new_committee)
        db.event.listen(Actions, "after_insert", new_action)


        # Test committee dictionary
        self.test_committee_dict = {
            "id" : "testcommittee1",
            "title": "testcommittee1",
            "description": "Test Description",
            "location": "Test Location",
            "meeting_time": "1300",
            "meeting_day": 2,
            "head": "testuser",
            "committee_img": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        }

        # Test action dict
        self.test_action_dict = {
            "token": self.user_token,
            "charge": 10,
            "assigned_to": "testuser",
            "title": "test title",
            "description": "test description"
        }

    def teardown_method(self):
        self.socketio.disconnect()

    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()


    # Test when a user is made committee head on create.
    def test_new_committee(self):
        self.test_committee_dict["token"] = self.admin_token
        self.socketio.emit('create_committee', self.test_committee_dict)
        self.socketio.emit('get_notifications', {"token": self.user_token})
        received = self.socketio.get_received()

        expected = {
            'destination': 'testcommittee1', 
            'id': 1, 
            'type': 'MadeCommitteeHead',
            'user': 'testuser'
        }
        assert received[2]["args"][0][0] == expected

    
    # Test when a user is assigned to an action.
    def test_new_action(self):
        self.socketio.emit('create_action', self.test_action_dict)
        received = self.socketio.get_received()

        expected = {
            'destination': '1',
            'user': 'testuser',
            'id': 1,
            'type': 'AssignedToAction'
        }
        assert received[0]["args"][0][0] == expected


    # Test when a user sends a request to join a committee.
    def test_new_request(self):
        test_invitation = {
            'committee_id': 'testcommittee',
            'user_id': 'testuser2',
            'token': self.user_token_two
        }
        self.socketio.emit('add_member_committee', test_invitation)
        self.socketio.emit('get_notifications', {"token": self.user_token})
        received = self.socketio.get_received()

        expected = {
            'id': 1,
            'destination': '1',
            'type': 'UserRequest',
            'user': 'testuser'
        }
        assert received[1]["args"][0][0] == expected


    # Test when a user is mentioned in a note.
    def test_new_note(self):
        user_data = {
            "token": self.user_token,
            "action": 10,
            "description": "@testuser"
        }

        self.socketio.emit('create_note', user_data)
        received = self.socketio.get_received()
        
        expected = {
            'destination': '1',
            'id': 1,
            'type': 'MentionedInNote',
            'user': 'testuser'
        }
        assert received[0]["args"][0][0] == expected
