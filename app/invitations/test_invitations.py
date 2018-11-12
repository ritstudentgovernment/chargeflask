"""
filename: test_invitations.py
description: Tests for Invitations
created by: Omar De La Hoz
created on: 10/19/17
"""

import pytest
import config
from app.invitations.models import Invitations
from app import app, db, socketio
from app.users.models import Users
from mock import patch, MagicMock
from app.committees.models import Committees
from app.invitations.invitations_response import Response
from app.notifications.controllers import new_request, new_committee
from flask_sqlalchemy import SQLAlchemy



class TestInvitations(object):

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
        db.event.remove(Invitations, "after_insert", new_request)
        self.socketio = socketio.test_client(app);
        self.socketio.connect()

    def setup_method(self, method):
        db.drop_all()
        db.create_all()
        self.user_data = {"user_id": "testuser",
                          "committee_id": "testcommittee"}

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
        self.user_token = user.generate_auth()
        self.user_token = self.user_token.decode('ascii')
        self.user = user

        # Create second normal user for tests.
        user2 = Users(id = "testuser2")
        user2.first_name = "Test2"
        user2.last_name = "User2"
        db.session.add(user2)
        db.session.commit()

        self.user_token2 = user2.generate_auth()
        self.user_token2 = self.user_token2.decode('ascii')
        self.user2 = user2

        # Create a test committee.
        self.committee = Committees(id = "testcommittee")
        self.committee.title = "Test Committee"
        self.committee.description = "Test Description"
        self.committee.location = "Test Location"
        self.committee.meeting_time = "1300"
        self.committee.meeting_day =  2
        self.committee.head = "adminuser"
        db.session.add(self.committee)
        db.session.commit()

        self.invite = Invitations(id = 5)
        self.invite.user_name =  "newuser1"
        self.invite.committee = self.committee
        self.invite.committee_id = "testcommittee"
        self.invite.isInvite = False

    @classmethod
    def teardown_class(self):
        db.event.listen(Committees, "after_insert", new_committee)
        db.event.listen(Invitations, "after_insert", new_request)
        db.session.close()
        db.drop_all()
        self.socketio.disconnect()


    # Test sending a request to join a committee.
    def test_request_successful(self):
        self.user_data["token"] = self.user_token
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.RequestSent


    # Test sending a request to join a committee
    # but request already exists.
    def test_request_exists(self):
        self.user_data["token"] = self.user_token

        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.RequestExists

    # Test send invitation to new user.
    def test_invite_successful(self):
        self.user_data["token"] = self.admin_token
        self.user_data["user_id"] = "newuser1"
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InviteSent


    # Test invitation has already been sent.
    def test_invite_exists(self):
        self.user_data["token"] = self.admin_token
        self.user_data["user_id"] = "newuser1"
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InviteExists



    # Test view a request success.
    def test_get_invite_success(self):
        db.session.add(self.invite)
        db.session.commit()

        request_data = {
    		"token": self.admin_token,
    		"invitation_id": 5,
            "status": True
        }

        invite_data = {
    		"committee_head": "adminuser",
    		"committee_id": "testcommittee",
    		"committee_title": "Test Committee",
    		"current_user": "adminuser",
    		"invite_user": "newuser1",
    		"is_invite": False
    	}

        self.socketio.emit("get_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == invite_data


    # Test get non existent invitation.
    def test_get_invite_404(self):
    	request_data = {
    		"token": self.admin_token,
    		"invitation_id": 9999
    	}

    	self.socketio.emit("get_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.InviteDoesntExist


    # Test get with non-existent user.
    def test_get_invite_nouser(self):
        db.session.add(self.invite)
        db.session.commit()

        request_data = {
    		"token": "",
    		"invitation_id": 5
    	}

        self.socketio.emit("get_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.NotAuthenticated


    # Test get invite not allowed.
    def test_get_invite_noperms(self):
        db.session.add(self.invite)
        db.session.commit()
        request_data = {
    		"token": self.user_token2,
    		"invitation_id": 5
    	}

        self.socketio.emit("get_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.IncorrectPerms


    # Test set invitation doesn't exist.
    def test_set_invite_404(self):

    	request_data = {
    		"token": self.user_token2,
    		"invitation_id": 9999,
    		"status": True
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.InviteDoesntExist


    # Test set user doesn't exist.
    def test_set_invite_nouser(self):
        db.session.add(self.invite)
        db.session.commit()
        request_data = {
    		"token": "",
    		"invitation_id": 5,
    		"status": True
    	}

        self.socketio.emit("set_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.NotAuthenticated


    # Test set no status.
    def test_set_invite_status404(self):
        db.session.add(self.invite)
        db.session.commit()
        request_data = {
    		"token": self.admin_token,
    		"invitation_id": 5
    	}

        self.socketio.emit("set_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InvalidStatus


    # Test incorrect status type.
    def test_set_invite_incorstatus(self):
        db.session.add(self.invite)
        db.session.commit()
        request_data = {
    		"token": self.admin_token,
    		"invitation_id": 5,
    		"status": "True"
    	}

        self.socketio.emit("set_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InvalidStatus


    # Test user shouldn't set invitation.
    def test_set_invite_noperms(self):
        db.session.add(self.invite)
        db.session.commit()
        request_data = {
    		"token": self.user_token,
    		"invitation_id": 5,
    		"status": True
    	}

        self.socketio.emit("set_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.IncorrectPerms


    # Test set invitation True.
    def test_set_invite_success(self):
        db.session.add(self.invite)
        db.session.commit()

        request_data = {
    		"token": self.admin_token,
    		"invitation_id": 5,
    		"status": True
    	}

        self.socketio.emit("set_invitation", request_data)
        received = self.socketio.get_received()
        assert received[1]["args"][0] == Response.InviteAccept


    # Test set invitation False.
    def test_set_invite_false(self):
        db.session.add(self.invite)
        db.session.commit()

        request_data = {
            "token": self.admin_token,
            "invitation_id": 5,
            "status": False

        }

        self.socketio.emit("set_invitation", request_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InviteDeny
