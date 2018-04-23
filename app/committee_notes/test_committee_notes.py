"""
filename: test_committees.py
description: Tests for Committees.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/23/18
"""

import pytest
import config
from app import app, db, socketio
from app.committee_notes.committee_notes_response import Response
from app.committees.models import Committees
from app.committee_notes.models import *
from app.users.permissions import Permissions
from app.charges.models import *
from app.users.models import Users
from flask_socketio import SocketIOTestClient
from flask_sqlalchemy import SQLAlchemy

class TestCommitteeNotes(object):

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

        committee_note = CommitteeNotes(id = 10)
        committee_note.author = "testuser"
        committee_note.description = "Test Note"
        committee_note.committee = "testcommittee"
        committee_note.hidden = False
        self.committee_note = committee_note
        db.session.add(self.committee_note)
        db.session.commit()

    # Test when creating a note
    def test_create_committee_note(self):
        user_data = {"token": self.admin_token,
                     "committee": "testcommittee",
                     "description": "Test Note"}

        self.socketio.emit('create_committee_note', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    # Test when creating a note with an invalid action
    def test_create_committee_note_no_committee(self):
        user_data = {"token": self.admin_token,
                     "committee": "ugh",
                     "description": "New Description"}

        self.socketio.emit('create_committee_note', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.CommitteeDoesntExist

    # Test when a note is created by a committee head
    def test_create_committee_note_charge_head(self):
        user_data = {"token": self.user_token,
                     "committee": "testcommittee",
                     "description": "New Description"}

        self.socketio.emit('create_committee_note', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    # Test when a charge is created by a non authorized user
    def test_create_committee_note_not_auth(self):
        user_data = {"token": self.user_token2,
                     "committee": "testcommittee",
                     "description": "New Description"}

        self.socketio.emit('create_committee_note', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrNotAuth
