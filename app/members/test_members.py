"""
filename: test_members.py
description: Tests for Membership.
created by: Omar De La Hoz
created on: 10/05/17
"""

import pytest
import config
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
		app.config['SQLALCHEMY_DATABASE'] = config.SQLALCHEMY_TEST_DATABASE_URI
		self.app = app.test_client()
		self.db = db
		self.db.session.close()
		self.db.drop_all()
		self.db.create_all()
		self.socketio = socketio.test_client(app);
		self.socketio.connect()


	def setup_method(self, method):
		self.db.drop_all()
		self.db.create_all()

		self.user_data = {"user_id": "testuser",
						  "committee_id": "testcommittee"}

		# Create admin user for tests.
		self.admin = Users(id = "adminuser")
		self.admin.first_name = "Admin"
		self.admin.last_name = "User"
		self.admin.email = "adminuser@test.com"
		self.admin.is_admin = True
		self.db.session.add(self.admin)
		self.db.session.commit()
		self.admin_token = self.admin.generate_auth()
		self.admin_token = self.admin_token.decode('ascii')

		# Create normal user for tests.
		self.user = Users(id = "testuser")
		self.user.first_name = "Test1"
		self.user.last_name = "User"
		self.user.email = "testuser@test.com"
		self.user.is_admin = False
		db.session.add(self.user)
		db.session.commit()
		self.user_token = self.user.generate_auth()
		self.user_token = self.user_token.decode('ascii')

		# Create a test committee.
		self.committee = Committees(id = "testcommittee")
		self.committee.title = "Test Committee"
		self.committee.description = "Test Description"
		self.committee.location = "Test Location"
		self.committee.meeting_time = "1200"
		self.committee.meeting_day = 2
		self.committee.head = "adminuser"
		self.committee.members.append(self.user)
		db.session.add(self.committee)
		db.session.commit()

	@classmethod
	def teardown_class(self):
		self.db.session.close()
		self.db.drop_all()
		self.socketio.disconnect()


	# Test get members of nonexistent committee.
	def test_get_committee_members_nonexistent(self):
		self.socketio.emit("get_members", "nonexistent")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.ComDoesntExist


	# Test get members of committee.
	def test_get_committee_members(self):
		self.socketio.emit("get_members", "testcommittee")
		received = self.socketio.get_received()
		commitee = received[0]["args"][0]
		assert commitee["committee_id"] == "testcommittee"
		assert (commitee["members"] == [{'id': 'testuser'}])

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
		self.user_data["user_id"] = self.user.id
		self.socketio.emit("remove_member_committee", self.user_data)
		received = self.socketio.get_received()
		print (received)
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


	# Test adding a member raises an Exception.
	@patch('app.committees.models.Committees.members')
	def test_add_exception(self, mock_obj):
		mock_obj.append.side_effect = Exception("User couldn't be added.")
		self.user_data["token"] = self.admin_token
		self.socketio.emit("add_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.AddError


	# Test removing a member raises an Exception.
	@patch('app.committees.models.Committees.members')
	def test_remove_exception(self, mock_obj):
		mock_obj.remove.side_effect = Exception("User couldn't be removed.")
		self.user_data["token"] = self.admin_token
		self.socketio.emit("remove_member_committee", self.user_data)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.RemoveError
