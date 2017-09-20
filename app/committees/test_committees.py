"""
filename: test_committees.py
description: Tests for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/19/17
"""

import pytest
from app import app, db, socketio
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

	# Test when an admin creates a committee.
	def test_admin_create_committee(self):

		test_committee = {"token": self.admin_token, 
						  "committee_title": "Test Committee",
						  "committee_description": "Test Description",
						  "committee_location": "Test Location",
						  "head_id": "adminuser"}

		self.socketio.emit('create_committee', test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'success': 'Committee succesfully created'}

	# Test when creating a committee that already exists.
	def test_create_committee_exists(self):

		test_committee = {"token": self.admin_token, 
						  "committee_title": "Test Committee",
						  "committee_description": "Test Description",
						  "committee_location": "Test Location",
						  "head_id": "adminuser"}

		self.socketio.emit('create_committee', test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error', "Committee already exists."}

	# Test when a non-admin user tries to create a committee.
	def test_non_admin_create_committee(self):

		test_committee = {"token": self.user_token, 
						  "committee_title": "Test Petition",
						  "committee_description": "Test Description",
						  "committee_location": "Test Location",
						  "head_id": "adminuser"}

		self.socketio.emit('create_committee', test_committee)
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error', "User doesn't exist or is not admin."}

	# Test get an specific committee.
	def test_get_committee(self):

		test_committee = {"committee_id": "testcommittee", 
						  "committee_title": "Test Committee",
						  "committee_description": "Test Description",
						  "committee_location": "Test Location",
						  "committee_head": "adminuser"}

		self.socketio.emit('get_committee', "testcommittee")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == test_committee

	# Test getting a nonexistent committee
	def test_get_nonexistent_committee(self):
		self.socketio.emit('get_committee', "dontexist")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error', "Committee doesn't exist."}