"""
filename: tests.py
description: Tests for Users.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/12/17
"""

import unittest
import coverage
from app import app, socketio
from app.users.models import Users


cov = coverage.coverage(branch=True)
cov.start()

class TestUser(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		cov.stop()
		cov.report()

	def test_connect(self):
		client = socketio.test_client(app)
		received = client.get_received()
		self.assertEqual(len(received), 0)
		client.disconnect()

	def test_login(self):
		client = socketio.test_client(app)
		client.emit('auth', {"username": "", "password": ""});
		received = client.get_received()
		self.assertEqual(len(received[0]['args']), 1)
		client.disconnect()

if __name__ == '__main__':
    unittest.main()
