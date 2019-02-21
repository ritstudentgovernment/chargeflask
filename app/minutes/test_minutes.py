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
from app.minutes.models import Minutes
from app.minutes.minutes_response import Response
from app.minutes.models import Minutes, Topics
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

        # Create normal member for tests.
        self.normal_member = Users(id = "testuser")
        self.normal_member.first_name = "Test1"
        self.normal_member.last_name = "User"
        self.normal_member.email = "testuser@test.com"
        self.normal_member.is_admin = False
        db.session.add(self.normal_member)
        db.session.commit()
        self.normal_member_token = self.normal_member.generate_auth()
        self.normal_member_token = self.normal_member_token.decode('ascii')

        # Create normal minute taker for tests.
        self.minute_taker = Users(id = "test2user")
        self.minute_taker.first_name = "Test2"
        self.minute_taker.last_name = "User"
        self.minute_taker.email = "test2user@test.com"
        self.minute_taker.is_admin = False
        db.session.add(self.minute_taker)
        db.session.commit()
        self.minute_taker_token = self.minute_taker.generate_auth()
        self.minute_taker_token = self.minute_taker_token.decode('ascii')

        # Create normal minute taker for tests.
        self.not_member = Users(id = "test3user")
        self.not_member.first_name = "Test3"
        self.not_member.last_name = "User"
        self.not_member.email = "test3user@test.com"
        self.not_member.is_admin = False
        db.session.add(self.not_member)
        db.session.commit()
        self.not_member_token = self.not_member.generate_auth()
        self.not_member_token = self.not_member_token.decode('ascii')

        # Create a test committee.
        self.committee = Committees(id = "testcommittee")
        self.committee.title = "Test Committee"
        self.committee.description = "Test Description"
        self.committee.location = "Test Location"
        self.committee.meeting_time = "1200"
        self.committee.meeting_day = 2
        self.committee.head = "adminuser"

        # Add user to committee as normal member.
        normal_role = Members(role= Roles.NormalMember)
        normal_role.member = self.normal_member
        self.committee.members.append(normal_role)

        minute_taker_role = Members(role= Roles.MinuteTaker)
        minute_taker_role.member = self.minute_taker
        self.committee.members.append(minute_taker_role)

        db.session.add(self.committee)

        self.user_data = {
            "token": self.admin_token,
            "committee_id": self.committee.id,
            "title": "New Minute",
            "date": 565745465,
            "private": False
        }

        self.minute = Minutes(title="Test Minute", date= 282827, private= True)
        self.topic = Topics(topic="Topic", body="Body")
        self.minute.topics.append(self.topic)
        self.committee.minutes.append(self.minute)

        db.session.commit()
    
    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        db.event.listen(Committees, "after_insert", new_committee)
        self.socketio.disconnect()
    
    def test_get_minutes(self):
        self.socketio.emit("get_minutes", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        print(response)
        result = [{
            'id': 1,
            'title': 'Test Minute',
            'date': 282827,
            'committee_id': 'testcommittee',
            'topics': [{'topic': 'Topic', 'body': 'Body'}]
        }]
        assert response == result
    
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
        assert response == Response.CommitteeDoesntExist
    
    def test_create_minute_no_title(self):
        del self.user_data['title']
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddMinuteError
    
    def test_create_minute_no_date(self):
        del self.user_data['date']
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddMinuteError
    
    def test_create_minute_normal_user_public(self):
        self.user_data["token"] = self.normal_member_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_create_minute_normal_member_private(self):
        self.user_data["private"] = True
        self.user_data["token"] = self.normal_member_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_create_minute_minute_taker_public(self):
        self.user_data["token"] = self.minute_taker_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError

    # Admin create public minute
    def test_create_minute_admin_public(self):
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddMinuteSuccess
    
    def test_create_minute_minute_taker_private(self):
        self.user_data["private"] = True
        self.user_data["token"] = self.minute_taker_token
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddMinuteSuccess
    
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
        assert response == Response.AddMinuteSuccess
    
    @patch('app.minutes.controllers.db.session.add')
    def test_create_minute_exception(self, mock_obj):
        mock_obj.side_effect = Exception("Minute couldn't be added.")
        self.user_data["token"] = self.admin_token
        self.user_data["committee_id"] = self.committee.id
        self.socketio.emit("create_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddMinuteError
    
    def test_create_minute_topics_no_user(self):
        self.user_data["token"] = ""
        self.user_data["minute_id"] = self.minute.id
        self.user_data["topics"] = [
            {
                "topic": "Topic One",
                "body": "Body of topic."
            }
        ]

        self.socketio.emit("create_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_create_minute_topics_no_minute(self):
        self.user_data["minute_id"] = -1
        self.user_data["topics"] = [
            {
                "topic": "Topic One",
                "body": "Body of topic."
            }
        ]

        self.socketio.emit("create_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.MinuteDoesntExist
    
    def test_create_minute_topics_no_topics(self):
        self.user_data["minute_id"] = self.minute.id
        self.socketio.emit("create_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.InvalidData
    
    def test_create_minute_topics_no_perm(self):
        self.user_data["token"] = self.normal_member_token
        self.user_data["minute_id"] = self.minute.id
        self.user_data["topics"] = [
            {
                "topic": "Topic One",
                "body": "Body of topic."
            }
        ]

        self.socketio.emit("create_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    
    def test_create_minute_topics(self):
        self.user_data["minute_id"] = self.minute.id
        self.user_data["topics"] = [
            {
                "topic": "Topic One",
                "body": "Body of topic."
            }
        ]

        self.socketio.emit("create_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddTopicSuccess
    

    @patch('app.minutes.models.Minutes.topics')
    def test_create_minute_topics_exception(self, mock_obj):
        mock_obj.append.side_effect = Exception("Topics couldn't be added.")
        self.user_data["token"] = self.admin_token
        self.user_data["minute_id"] = self.minute.id
        self.user_data["topics"] = [
            {
                "topic": "Topic One",
                "body": "Body of topic."
            }
        ]

        self.socketio.emit("create_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.AddTopicError
    
    def test_delete_minute_topics_no_user(self):
        self.user_data["token"] = ""
        self.user_data["topics"] = [
            {
                "id": self.topic.id,
                "topic": "Topic",
                "body": "Body"
            }
        ]

        self.socketio.emit("delete_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_delete_minute_topics_no_topics(self):
        self.user_data["token"] = self.admin_token
        self.socketio.emit("delete_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.InvalidData
    
    def test_delete_minute_topics_not_topic_id(self):
        self.user_data["token"] = self.admin_token
        self.user_data["topics"] = [
            {
                "topic": "Topic",
                "body": "Body"
            }
        ]
        self.socketio.emit("delete_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.InvalidData
    
    def test_delete_minute_topics_no_perm(self):
        self.user_data["token"] = self.normal_member_token
        self.user_data["topics"] = [
            {
                "id": self.topic.id,
                "topic": "Topic",
                "body": "Body"
            }
        ]

        self.socketio.emit("delete_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_delete_minute_topics_success(self):
        self.user_data["token"] = self.admin_token
        self.user_data["topics"] = [
            {
                "id": self.topic.id,
                "topic": "Topic",
                "body": "Body"
            }
        ]

        self.socketio.emit("delete_minute_topics", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.DeleteTopicSuccess
    
    def test_get_minute(self):
        
        user_data = {
            "token": self.normal_member_token,
            "minute_id": self.minute.id
        }

        result = {
            'id': 1,
            'title': 'Test Minute',
            'date': 282827,
            'committee_id': 'testcommittee',
            'topics': [{'topic': 'Topic', 'body': 'Body'}]
        }

        self.socketio.emit('get_minute', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == result
    
    def test_get_minute_doesnt_exist(self):
        user_data = {
            "token": self.normal_member_token,
            "minute_id": -1
        }

        self.socketio.emit('get_minute', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.MinuteDoesntExist

    def test_get_minute_no_user(self):
        user_data = {
            "token": '',
            "minute_id": self.minute.id
        }

        self.socketio.emit('get_minute', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UserDoesntExist

    def test_get_minute_no_minute(self):
        self.socketio.emit('get_minute', self.user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.MinuteDoesntExist

    def test_get_minute_notmember_private(self):
        user_data = {
            "token": self.not_member_token,
            "minute_id": self.minute.id,
            "private": True,
            'committee_id': ''
        }
        self.socketio.emit('get_minute', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.PermError
