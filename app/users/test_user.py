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
from app.users.controllers import login_from_acs
from flask_socketio import SocketIOTestClient
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from app.users.users_response import Response



class TestUser(object):

    @classmethod
    def setup_class(self):
        self.app = app.test_client()

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = "test_key"
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

    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        self.socketio.disconnect()

    # Test empty login.
    def test_empty_login(self):
        self.socketio.emit("auth", {"username":"","password":""})
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AuthError

    # Test invalid datatype
    def test_invalid_datatype(self):
        self.socketio.emit("auth", "invalid_datatype")
        received = self.socketio.get_received()
        assert received[0]["args"][0] == {'error': 'Please check data type.'}

    # Test incorrect login.
    def test_incorrect_login(self):
        self.socketio.emit("auth", {"username":"incorrect","password":"incorrect"})
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AuthError

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

    # Test verify_auth when user doesnt exist.
    def test_verify_user_doesnt_exist(self):
        invalid_token = {"token": "thisisinvalid"}
        self.socketio.emit("verify_auth", invalid_token)

        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AuthError

    # Test error in shibboleth login.
    def test_login_shib_error(self):
        with app.app_context():
            res = login_from_acs({'errors': "thisisanerror"})
            assert res.get_json() == {'errors': 'thisisanerror'}

    # Test shibboleth login failed.
    def test_login_shib_failed(self):
        with app.app_context():
            res = login_from_acs({})
            assert res.get_json() == {'error': 'login failed'}

    def test_login_shib_success(self):
        with app.test_request_context():
            attributes = [[[],[""]],[],[[],[""]],[[],[""]],[],[[],[""]]]
            res = login_from_acs({'logged_in': True, 'attributes': attributes})
            assert res.status == "302 FOUND"
