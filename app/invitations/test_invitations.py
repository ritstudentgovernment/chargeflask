"""
filename: test_invitations.py
description: Tests for Invitations
created by: Omar De La Hoz
created on: 10/19/17
"""

import pytest
from app import app, db, socketio
from app.users.models import Users
from mock import patch, MagicMock
from app.committees.models import Committees
from app.invitations.invitations_response import Response

class TestInvitations(object):

    @classmethod
    def setup_class(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.db = db
        self.db.session.close()
        self.db.drop_all()
        self.db.create_all()
        self.socketio = socketio.test_client(app);
        self.socketio.connect()

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

        # Create second normal user for tests.
        user2 = Users(id = "testuser2")
        user2.first_name = "Test2"
        user2.last_name = "User2"
        db.session.add(user2)
        db.session.commit()

        self.user_token2 = user2.generate_auth()
        self.user_token2 = self.user_token2.decode('ascii')

        # Create a test committee.
        committee = Committees(id = "testcommittee")
        committee.title = "Test Committee"
        committee.description = "Test Description"
        committee.location = "Test Location"
        committee.meeting_time = "1300"
        committee.meeting_day =  2
        committee.head = "adminuser"
        db.session.add(committee)
        db.session.commit()


    @classmethod
    def teardown_class(self):
        self.db.session.close()
        self.db.drop_all()


    def setup_method(self, method):
        self.user_data = {"user_id": "testuser",
                          "committee_id": "testcommittee"}

    
    def teardown_method(self, method):
        self.user_data = None

    
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
        assert received[0]["args"][0] == Response.RequestExists

    
    # Test failed to add request.
    @patch('app.invitations.models.Invitations')
    @patch('app.mail.send')
    def test_request_error(self, mock_obj, mock_mail):
        mock_obj.side_effect = Exception("Invitation couldn't be created.")
        mock_mail.side_effect = Exception("Mail couldn't be sent.")

        self.user_data["token"] = self.user_token2
        self.user_data["user_id"] = ""
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.RequestError


    # Test send invitation to new user.
    def test_invite_successful(self):
        self.user_data["token"] = self.admin_token
        self.user_data["user_id"] = "newuser"
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InviteSent


    # Test invitation has already been sent.
    def test_invite_exists(self):
        self.user_data["token"] = self.admin_token
        self.user_data["user_id"] = "newuser"
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InviteExists


    # Test invitation request failed to add invitation.
    @patch('app.invitations.models.Invitations')
    @patch('app.mail.send')
    def test_invite_exception(self, mock_obj, mock_mail):
        self.user_data["token"] = self.admin_token
        self.user_data["user_id"] = "willfail"
        mock_obj.side_effect = Exception("Invitation couldn't be created.")
        mock_mail.side_effect = Exception("Mail couldn't be sent.")
        self.socketio.emit("add_member_committee", self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.InviteError


    # Test view a request success.
    def test_get_invite_success(self):

    	request_data = {
    		"token": self.admin_token,
    		"invitation_id": 1 
    	}

    	invite_data = {
    		"committee_head": "adminuser",
    		"committee_id": "testcommittee",
    		"committee_title": "Test Committee",
    		"current_user": "adminuser",
    		"invite_user": "testuser",
    		"is_invite": False
    	}

    	self.socketio.emit("get_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == invite_data


    # Test get non existent invitation.
    def test_get_invite_404(self):
    	request_data = {
    		"token": self.admin_token,
    		"invitation_id": 20
    	}

    	self.socketio.emit("get_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.InviteDoesntExist


    # Test get with non-existent user.
    def test_get_invite_nouser(self):
    	request_data = {
    		"token": "",
    		"invitation_id": 1
    	}

    	self.socketio.emit("get_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.NotAuthenticated


    # Test get invite not allowed.
    def test_get_invite_noperms(self):
    	request_data = {
    		"token": self.user_token2,
    		"invitation_id": 1
    	}

    	self.socketio.emit("get_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.IncorrectPerms


    # Test set invitation doesn't exist.
    def test_set_invite_404(self):
    	request_data = {
    		"token": self.user_token2,
    		"invitation_id": 10,
    		"status": True
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.InviteDoesntExist


    # Test set user doesn't exist.
    def test_set_invite_nouser(self):
    	request_data = {
    		"token": "",
    		"invitation_id": 1,
    		"status": True
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.NotAuthenticated


    # Test set no status.
    def test_set_invite_status404(self):
    	request_data = {
    		"token": self.admin_token,
    		"invitation_id": 1
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.InvalidStatus


    # Test incorrect status type.
    def test_set_invite_incorstatus(self):
    	request_data = {
    		"token": self.admin_token,
    		"invitation_id": 1,
    		"status": "True"
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.InvalidStatus


    # Test user shouldn't set invitation.
    def test_set_invite_noperms(self):
    	request_data = {
    		"token": self.user_token,
    		"invitation_id": 1,
    		"status": True
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[0]["args"][0] == Response.IncorrectPerms

    
    # Test set invitation True.
    def test_set_invite_success(self):
    	request_data = {
    		"token": self.admin_token,
    		"invitation_id": 1,
    		"status": True
    	}

    	self.socketio.emit("set_invitation", request_data)
    	received = self.socketio.get_received()
    	assert received[2]["args"][0] == Response.InviteAccept
