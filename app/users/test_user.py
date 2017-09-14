"""
filename: tests.py
description: Tests for Users.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/12/17
"""


import pytest
from mock import patch, MagicMock
from pytest_mock import mocker
from app import app, db, socketio
from app.users.models import Users
from app.users.controllers import login_user
from flask_socketio import SocketIOTestClient


class TestUser(object):

	@classmethod
	def setup_class(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.db = db
		self.db.create_all()
		self.socketio = socketio.test_client(app);
		self.socketio.connect()

	@classmethod 
	def teardown_class(self):
		self.socketio.disconnect()


	# Test empty login.
	def test_empty_login(self):
		self.socketio.emit("auth", {"username":"","password":""})
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error': 'Authentication error.'}

	# Test incorrect login.
	def test_incorrect_login(self):
		self.socketio.emit("auth", {"username":"incorrect","password":"incorrect"})
		received = self.socketio.get_received()
		assert received[0]["args"][0] == {'error': 'Authentication error.'}