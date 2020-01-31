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
from app.minutes.models import Minutes
from app.charges.models import Charges
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
            "body": "This is a test body.",
            "date": 565745465,
            "private": False
        }

        # Create a test charge.
        charge = Charges(id = 10)
        charge.author = "testuser"
        charge.title = "Test Charge"
        charge.description = "Test Description"
        charge.committee = "testcommittee"
        charge.paw_links = "https://testlink.com"
        charge.priority = 0
        charge.status = 0
        self.charge = charge
        db.session.add(charge)

        # Create a new test charge.
        new_charge = Charges(id = 11)
        new_charge.author = "testuser"
        new_charge.title = "Test Charge"
        new_charge.description = "Test Description"
        new_charge.committee = "testcommittee"
        new_charge.paw_links = "https://testlink.com"
        new_charge.priority = 0
        new_charge.status = 0
        self.new_charge = new_charge
        db.session.add(new_charge)

        self.minute = Minutes(title="Test Minute", body="TestBody", date= 282827, private= True)
        self.minute.charges.append(self.charge)
        self.committee.minutes.append(self.minute)

        db.session.commit()
    
    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        db.event.listen(Committees, "after_insert", new_committee)
        self.socketio.disconnect()
    
    def test_get_minutes_no_user(self):
        self.user_data["token"] = ""
        self.socketio.emit("get_minutes", self.user_data)

        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_get_minutes_no_committee(self):
        self.user_data["committee_id"] = ""
        self.socketio.emit("get_minutes", self.user_data)

        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.CommitteeDoesntExist
    
    def test_get_minutes_not_member(self):
        self.user_data["token"] = self.not_member_token
        self.socketio.emit("get_minutes", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == []
    
    def test_get_minutes_success(self):
        self.socketio.emit("get_minutes", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        
        result = [{
            'id': 1,
            'title': 'Test Minute',
            'body': 'TestBody',
            'date': 282827,
            'private': True,
            'committee_id': 'testcommittee',
            'charges': [{'id': 10, 'title': "Test Charge"}]
        }]
        assert response == result
    
    def test_get_minute_success(self):
        
        user_data = {
            "token": self.normal_member_token,
            "minute_id": self.minute.id
        }

        result = {
            'id': 1,
            'title': 'Test Minute',
            'body': 'TestBody',
            'date': 282827,
            'private': True,
            'committee_id': 'testcommittee',
            'charges': [{'id': 10, 'title': "Test Charge"}]
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
        assert response == Response.AddMinuteSuccess
    
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
    
    def test_create_minute_with_charges(self):
        self.user_data["charges"] = [self.new_charge.id]
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
    
    def test_delete_minute_no_user(self):
        del self.user_data['token']
        self.user_data["minute_id"] = self.minute.id
        self.socketio.emit("delete_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_delete_minute_no_minute(self):
        self.socketio.emit("delete_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.MinuteDoesntExist
    
    def test_delete_minute_no_perm(self):
        self.user_data["token"] = self.normal_member_token
        self.user_data["minute_id"] = self.minute.id
        self.socketio.emit("delete_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_delete_minute_success(self):
        self.user_data["minute_id"] = self.minute.id
        self.socketio.emit("delete_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.DeleteMinuteSuccess
    
    @patch('app.minutes.controllers.db.session.delete')
    def test_delete_minute_exception(self, mock_obj):
        mock_obj.side_effect = Exception("Minute couldn't be deleted.")
        self.user_data["minute_id"] = self.minute.id
        self.socketio.emit("delete_minute", self.user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.DeleteMinuteError
    
    def test_edit_minute_admin(self):
        user_data = {
            "token": self.admin_token,
            "minute_id": self.minute.id,
            "title": "newtitle",
            "body": "newbody",
            "charges": [11] # Get rid of old charge and add new.
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.EditSuccess

    def test_edit_minute_committee_head(self):
        user_data = {
            "token": self.admin_token,
            "minute_id": self.minute.id
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.EditSuccess
    
    def test_edit_minute_minute_taker(self):
        user_data = {
            "token": self.minute_taker_token,
            "minute_id": self.minute.id
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.EditSuccess
    
    def test_edit_minute_no_user(self):
        user_data = {
            "token": "",
            "minute_id": self.minute.id
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.UserDoesntExist
    
    def test_edit_minute_doesnt_exist(self):
        user_data = {
            "token": self.admin_token,
            "minute_id": -1
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.MinuteDoesntExist
    
    def test_edit_minute_private_not_member(self):
        user_data = {
            "token": self.not_member_token,
            "minute_id": self.minute.id,
            "private": True,
            'committee_id': ''
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_edit_minute_private_minute_taker(self):
        user_data = {
            "token": self.minute_taker_token,
            "minute_id": self.minute.id,
            "private": False,
            'committee_id': ''
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.PermError
    
    def test_edit_minute_body_success(self):
        user_data = {
            "token": self.admin_token,
            "minute_id": self.minute.id,
            "body": "test_body",
        }
        self.socketio.emit("edit_minute", user_data)
        received = self.socketio.get_received()
        response = received[0]["args"][0]
        assert response == Response.EditSuccess
