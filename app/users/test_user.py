"""
filename: test_user.py
description: Tests for Users.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/12/17
"""


import pytest
import config
from mock import patch, MagicMock
from pytest_mock import mocker
from app import app, db, socketio
from app.users.models import Users
from app.users.controllers import login_user
from flask_socketio import SocketIOTestClient
from flask_sqlalchemy import SQLAlchemy



class TestUser(object):

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
	def setup_method(self, method):
		db.drop_all()
		db.create_all()

	@classmethod
	def teardown_class(self):
		db.session.close()
		db.drop_all()
		self.socketio.disconnect()

	# Test empty login.
	def test_empty_login(self):
		self.socketio.emit("auth", {"username":"","password":""})
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error': 'Authentication error.'}

	# Test invalid datatype
	def test_invalid_datatype(self):
		self.socketio.emit("auth", "invalid_datatype")
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error': 'Please check data type.'}

	# Test incorrect login.
	def test_incorrect_login(self):
		self.socketio.emit("auth", {"username":"incorrect","password":"incorrect"})
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error': 'Authentication error.'}

	# Correct login new user.
	@patch('ldap.initialize')
	def test_correct_login_new(self, mock_obj):

		# Prepare mock ldap.
		self.mocked_inst = mock_obj.return_value
		self.mocked_inst.bind_s = MagicMock()

		# Create expected ldap result.
		result_ldap = [('',{'uid': [b'test'], 'givenName': [b'Test'], 'sn': [b'User'], 'mail': [b'testuser@test.edu']})]
		self.mocked_inst.search_s.return_value = result_ldap

		self.socketio.emit("auth", {"username":"test","password":"testuser"})
		received = self.socketio.get_received()
		assert 'token' in received[0]["args"][0]

	# Correct login existing user.
	@patch('ldap.initialize')
	def test_correct_login(self, mock_obj):

		# Prepare mock ldap.
		self.mocked_inst = mock_obj.return_value
		self.mocked_inst.bind_s = MagicMock()

		# Create expected ldap result.
		result_ldap = [('',{'uid': [b'test'], 'givenName': [b'Test'], 'sn': [b'User'], 'mail': [b'testuser@test.edu']})]
		self.mocked_inst.search_s.return_value = result_ldap
		self.socketio.emit("auth", {"username":"test","password":"testuser"})

		# Request existing user.
		received = self.socketio.get_received()
		assert 'token' in received[0]["args"][0]

	@patch('ldap.initialize')
	def test_token_authentication(self, mock_obj):
		# Prepare mock ldap.
		self.mocked_inst = mock_obj.return_value
		self.mocked_inst.bind_s = MagicMock()

		# Create expected ldap result.
		result_ldap = [('',{'uid': [b'test'], 'givenName': [b'Test'], 'sn': [b'User'], 'mail': [b'testuser@test.edu']})]
		self.mocked_inst.search_s.return_value = result_ldap
		self.socketio.emit("auth", {"username":"test","password":"testuser"})

		# Request token.
		received = self.socketio.get_received()
		token = received[0]["args"][0]["token"]
