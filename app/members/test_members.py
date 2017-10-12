"""
filename: test_members.py
description: Tests for Membership.
created by: Omar De La Hoz
created on: 10/05/17
"""

import pytest
from app import app, db, socketio
from mock import patch, MagicMock
from app.users.models import Users
from app.committees.models import Committees
from flask_socketio import SocketIOTestClient
from app.members.members_response import Response

class TestMembers(object):

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

		# Create a test committee.
		committee = Committees(id = "testcommittee")
		committee.title = "Test Committee"
		committee.description = "Test Description"
		committee.location = "Test Location"
		committee.meeting_time = 1506008454327
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


	# Test get members of nonexistent committee.
	def test_get_committee_members_nonexistent(self):
		self.socketio.emit("get_members", "nonexistent")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.ComDoesntExist


	# Test get members of committee.
	def test_get_committee_members(self):
		self.socketio.emit("get_members", "testcommittee")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {"committee_id": "testcommittee", "members":[]}


	# Test add to committee when not admin.
	def test_add_to_committee_not_admin(self):
		self.user_data["token"] = self.user_token
		self.socketio.emit("add_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.RequestSent


	# Test add to committee when admin.
	def test_add_to_committee(self):
		self.user_data["token"] = self.admin_token
		self.socketio.emit("add_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[1]["args"][0] == Response.AddSuccess


	# Test add committee doesnt exist.
	def test_add_non_existent(self):
		self.user_data["token"] = self.admin_token
		self.user_data["committee_id"] = "nonexistent"
		self.socketio.emit("add_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.UserDoesntExist


	# Test trying to remove not admin.
	def test_remove_member_notadmim(self):
		self.user_data["token"] = self.user_token
		self.socketio.emit("remove_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.PermError


	# Test remove member not admin
	def test_remove_member_admin(self):
		self.user_data["token"] = self.admin_token
		self.socketio.emit("remove_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[1]["args"][0] == Response.RemoveSuccess


	# Test remove nonexistent member.
	def test_remove_member_nonexistent(self):
		self.user_data["token"] = self.admin_token
		self.user_data["user_id"] = "nonexistent"
		self.socketio.emit("remove_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.UserDoesntExist


	# Test remove member nonexistent committee.
	def test_remove_member_noncomm(self):
		self.user_data["token"] = self.admin_token
		self.user_data["committee_id"] = "nonexistent"
		self.socketio.emit("remove_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.UserDoesntExist
