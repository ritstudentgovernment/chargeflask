"""
filename: test_minutes.py
description: Tests for Minutes.
created by: Omar De La Hoz
created on: 02/13/19
"""

import pytest
import config
from app import app, db, socketio
from mock import patch, MagicMock
from app.users.models import Users
from app.members.models import Members, Roles
from app.committees.models import Committees
from flask_socketio import SocketIOTestClient
from app.minutes.minutes_response import Response
from app.notifications.controllers import new_committee
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

class TestMinutes(object):

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
        self.socketio = socketio.test_client(app)
        self.socketio.connect()
    
    @classmethod
    def setup_method(self, method):
        db.drop_all()
        db.create_all()

        # Create admin user for tests.
        admin = Users(id = "adminuser")
        admin.first_name = "Admin"
        admin.last_name = "User"
        admin.email = "adminuser@test.com"
        admin.is_admin = True
        db.session.add(admin)
        #db.session.expunge(admin)
        db.session.commit()
        self.admin_token = admin.generate_auth()
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

        # Create normal user2 for tests.
        self.user2 = Users(id = "test2user")
        self.user2.first_name = "Test2"
        self.user2.last_name = "User"
        self.user2.email = "test2user@test.com"
        self.user2.is_admin = False
        db.session.add(self.user2)
        db.session.commit()
        self.user2_token = self.user2.generate_auth()
        self.user2_token = self.user2_token.decode('ascii')

        # Create a test committee.
        self.committee = Committees(id = "testcommittee")
        self.committee.title = "Test Committee"
        self.committee.description = "Test Description"
        self.committee.location = "Test Location"
        self.committee.meeting_time = "1200"
        self.committee.meeting_day = 2
        self.committee.head = "adminuser"

        # Add user to committee as normal member.
        role = Members(role= Roles.NormalMember)
        role.member = self.user
        self.committee.members.append(role)

        role2 = Members(role= Roles.MinuteTaker)
        role2.member = self.user2
        self.committee.members.append(role2)

        db.session.add(self.committee)

        self.user_data = {
            "token": self.admin_token,
            "committee_id": self.committee.id,
            "title": "New Minute",
            "date": 565745465,
            "private": False
        }

        db.session.commit()
    
    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        db.event.listen(Committees, "after_insert", new_committee)
        self.socketio.disconnect()
    
    def test_create_minute_no_user(self):
        del self.user_data['token']
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_create_minute_no_committee(self):
        del self.user_data['committee_id']
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_create_minute_no_title(self):
        del self.user_data['title']
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddError
    
    def test_create_minute_no_date(self):
        del self.user_data['date']
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddError
    
    def test_create_minute_normal_user_public(self):
        self.user_data["token"] = self.user_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_create_minute_normal_member_private(self):
        self.user_data["private"] = True
        self.user_data["token"] = self.user_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_create_minute_minute_taker_public(self):
        self.user_data["token"] = self.user2_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError

    # Admin create public minute
    def test_create_minute_admin_public(self):
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddSuccess
    
    def test_create_minute_minute_taker_private(self):
        self.user_data["private"] = True
        self.user_data["token"] = self.user2_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddSuccess
    
    def test_create_minute_with_topics(self):
        self.user_data["topics"] = [
            {
                "topic": "Topic 1",
                "body": "This is the body of topic one."
            },
            {
                "topic": "Topic 2",
                "body": "This is the bod of topic two."
            }
        ]

        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddSuccess
    
    @patch('app.minutes.controllers.db.session.add')
    def test_create_minute_exception(self, mock_obj):
        mock_obj.side_effect = Exception("Minute couldn't be added.")
        self.user_data["token"] = self.admin_token
        self.user_data["committee_id"] = self.committee.id
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddError
