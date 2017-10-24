"""
filename: test_committees.py
description: Tests for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/19/17
"""

import pytest
from app import app, db, socketio
from app.committees.committees_response import Response
from app.committees.models import Committees
from app.users.models import Users
from flask_socketio import SocketIOTestClient

class TestCommittees(object):

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

	@classmethod
	def teardown_class(self):
		self.db.session.close()
		self.db.drop_all()
		self.socketio.disconnect()

	def setup_method(self, method):

		self.test_committee = {"title": "Test Committee",
						       "description": "Test Description",
						       "location": "Test Location",
						       "meeting_time": "1300",
						       "meeting_day": 2,
						       "head": "adminuser"}

	def teardown_method(self, method):
		self.test_committee = None

	# Test when an admin creates a committee.
	def test_admin_create_committee(self):

		self.test_committee["token"] = self.admin_token
		self.socketio.emit('create_committee', self.test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.AddSuccess

	# Test when creating a committee that already exists.
	def test_create_committee_exists(self):

		self.test_committee["token"] = self.admin_token
		self.socketio.emit('create_committee', self.test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.AddExists

	# Test create incorrect data type.
	def test_create_incorrect_type(self):
		self.test_committee["token"] = self.admin_token
		self.test_committee["title"] = "Incorrect Committee"
		self.test_committee["meeting_time"] = "incorrect_type"

		self.socketio.emit('create_committee', self.test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.AddError

	# Test when a non-admin user tries to create a committee.
	def test_non_admin_create_committee(self):

		self.test_committee["token"] = self.user_token
		self.socketio.emit('create_committee', self.test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.UsrDoesntExist

	# Test get an specific committee.
	def test_get_committee(self):

		self.test_committee["id"] = "testcommittee"
		self.test_committee["head_name"] = "Admin User"
		self.socketio.emit('get_committee', "testcommittee")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == self.test_committee

	# Test getting a nonexistent committee
	def test_get_nonexistent_committee(self):

		self.socketio.emit('get_committee', "dontexist")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.ComDoesntExist

	# Test admin editing a committee.
	def test_admin_edit_committee(self):
		edit_fields = {"token": self.admin_token, 
		               "id": "testcommittee",
		               "description": "New Description"}

		self.socketio.emit('edit_committee', edit_fields)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.EditSuccess

	# Test not admin editing a committee.
	def test_nonadmin_edit_committee(self):
		edit_fields = {"token": self.user_token, 
		               "id": "testcommittee",
		               "description": "New Description"}

		self.socketio.emit('edit_committee', edit_fields)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.UsrDoesntExist

	# Test edit nonexistent committee
	def test_edit_nonexistent(self):
		edit_fields = {"token": self.admin_token, 
		               "id": "nonexistent",
		               "description": "New Description"}

		self.socketio.emit('edit_committee', edit_fields)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.ComDoesntExist


	# Test editing incorrect data type.
	def test_edit_incorrect(self):
		edit_fields = {"token": self.admin_token, 
		               "id": "testcommittee",
		               "meeting_time": "incorrect_type"}

		self.socketio.emit('edit_committee', edit_fields)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == Response.EditError

	
	