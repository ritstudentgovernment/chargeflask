"""
filename: test_committees.py
description: Tests for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/19/17
"""

import pytest
import config
from app import app, db, socketio
from app.committees.committees_response import Response
from app.committees.models import Committees
from app.users.permissions import Permissions
from app.members.models import Members, Roles
from app.users.models import Users
from app.notifications.controllers import new_committee
from flask_socketio import SocketIOTestClient
import base64
from flask_sqlalchemy import SQLAlchemy


class TestCommittees(object):

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
        self.socketio = socketio.test_client(app);
        self.socketio.connect()



    @classmethod
    def setup_method(self, method):
        db.drop_all()
        db.create_all()

        self.test_committee_dict = {
            "id" : "testcommittee",
            "title": "testcommittee",
            "description": "Test Description",
            "location": "Test Location",
            "meeting_time": "1300",
            "meeting_day": 2,
            "head": "testuser",
            "committee_img": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        }
        self.test_committee = Committees(id = "testcommittee")
        self.test_committee.title = self.test_committee_dict["title"]
        self.test_committee.location = self.test_committee_dict["location"]
        self.test_committee.description = self.test_committee_dict["description"]
        self.test_committee.meeting_time = self.test_committee_dict["meeting_time"]
        self.test_committee.meeting_day = self.test_committee_dict["meeting_day"]
        self.test_committee.head = self.test_committee_dict["head"]
        com_img = base64.b64decode(self.test_committee_dict["committee_img"])
        self.test_committee.com_image = com_img

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
        self.test_user = user
        self.user_token = user.generate_auth()
        self.user_token = self.user_token.decode('ascii')

        #self.ddb.session.add(self.test_committee)
        #db.session.expunge(self.test_committee)

        #db.session.commit()

    @classmethod
    def teardown_class(self):
        db.session.close()
        db.drop_all()
        db.event.listen(Committees, "after_insert", new_committee)
        self.socketio.disconnect()



    # Test when an admin creates a committee.
    def test_admin_create_committee(self):
        self.test_committee_dict["token"] = self.admin_token
        self.socketio.emit('create_committee', self.test_committee_dict)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddSuccess

    # Test when creating a committee that already exists.
    def test_create_committee_exists(self):
        db.session.add(self.test_committee)
        db.session.commit()
        test_committee_dup = {
            "token": self.admin_token,
            "title": self.test_committee.title
        }
        test_committee_dup["token"] = self.admin_token
        self.socketio.emit('create_committee', test_committee_dup)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddExists

    # Test create incorrect data type.
    def test_create_incorrect_type(self):
        self.test_committee_dict["token"] = self.admin_token
        self.test_committee_dict["meeting_time"] = "incorrect type"

        self.socketio.emit('create_committee', self.test_committee_dict)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddError

    # Test create without a required field.
    def test_create_no_required_field(self):
        self.test_committee_dict["token"] = self.admin_token
        self.test_committee_dict.pop('meeting_time', None)

        self.socketio.emit('create_committee', self.test_committee_dict)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.AddError

    # Test when a non-admin user tries to create a committee.
    def test_non_admin_create_committee(self):

        self.test_committee_dict["token"] = self.user_token
        self.socketio.emit('create_committee', self.test_committee_dict)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrDoesntExist

    # Test get an specific committee.
    def test_get_committee(self):
        db.session.add(self.test_committee)
        db.session.commit()
        self.test_committee_dict["head_name"] = "Test1 User"
        self.test_committee_dict.pop('committee_img', None)

        self.socketio.emit('get_committee', "testcommittee")
        received = self.socketio.get_received()
        assert received[0]["args"][0] == self.test_committee_dict

    # Test getting a nonexistent committee
    def test_get_nonexistent_committee(self):

        self.socketio.emit('get_committee', "dontexist")
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.ComDoesntExist

    # Test admin editing a committee description.
    def test_admin_edit_committee_description(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": self.test_committee.id,
                       "description": "New Description"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess
        self.socketio.emit('get_committee', self.test_committee_dict["id"])
        received = self.socketio.get_received()
        assert received[0]["args"][0]["description"] == edit_fields["description"]

    # Test admin editing a committee meeting day.
    def test_admin_edit_committee_meeting_day(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": self.test_committee.id,
                       "meeting_day": 3}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess
        self.socketio.emit('get_committee', self.test_committee_dict["id"])
        received = self.socketio.get_received()
        assert received[0]["args"][0]["meeting_day"] == edit_fields["meeting_day"]

    
    # Test admin editing a committee meeting time.
    def test_admin_edit_committee_meeting_time(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": self.test_committee.id,
                       "meeting_time": "1500"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess
        self.socketio.emit('get_committee', self.test_committee_dict["id"])
        received = self.socketio.get_received()
        assert received[0]["args"][0]["meeting_time"] == edit_fields["meeting_time"]

    # Test admin editing a committee location.
    def test_admin_edit_committee_meeting_time(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": self.test_committee.id,
                       "location": "outside"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess
        self.socketio.emit('get_committee', self.test_committee_dict["id"])
        received = self.socketio.get_received()
        assert received[0]["args"][0]["location"] == edit_fields["location"]
    
    # Test admin editing a committee_head.
    def test_admin_edit_committee_head(self):
        membership = Members(role= Roles.CommitteeHead)
        membership.member = Users.query.filter_by(id= self.test_committee.head).first()
        self.test_committee.members.append(membership)
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {
            "token": self.admin_token,
            "id": self.test_committee.id,
            "head": "adminuser"
        }

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess
    
    # Test admin editing a committee head doesnt exist.
    def test_admin_edit_committee_head_noexist(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {
            "token": self.admin_token,
            "id": self.test_committee.id,
            "head": "noexist"
        }

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrDoesntExist

    # Test not admin editing a committee.
    def test_nonadmin_edit_committee(self):
        edit_fields = {"token": self.user_token,
                       "id": self.test_committee.id,
                       "description": "New Description"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.UsrDoesntExist

    # Test edit nonexistent committee
    def test_edit_nonexistent(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": "nonexistent",
                       "description": "New Description"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.ComDoesntExist


    # Test editing incorrect data type.
    def test_edit_incorrect(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": self.test_committee.id,
                       "meeting_time": "incorrect_type"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditError

    # Test change committee head.
    def test_change_head(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": self.test_committee.id,
                       "head": "testuser"}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess

    # Test disable committee.
    def test_disable_committee(self):
        db.session.add(self.test_committee)
        db.session.commit()

        edit_fields = {"token": self.admin_token,
                       "id": "testcommittee",
                       "enabled": False}

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess


    # Test change committee image
    def test_change_commiteimg(self):
        db.session.add(self.test_committee)
        db.session.commit()
        edit_fields = {
            "token": self.admin_token,
            "id": self.test_committee.id,
            "committee_img": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOz=="
        }

        self.socketio.emit('edit_committee', edit_fields)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.EditSuccess

    # Test get permissions of admin user.
    def test_admin_perms(self):
        db.session.add(self.test_committee)
        db.session.commit()

        user_data = {
            "token": self.admin_token,
            "id": self.test_committee.id,
        }
        self.socketio.emit('get_permissions', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Permissions.CanEdit

    # Test get permissions of committee head.
    def test_head_perms(self):
        db.session.add(self.test_committee)
        db.session.commit()

        user_data = {
            "token": self.user_token,
            "id": self.test_committee.id,
        }
        self.socketio.emit('get_permissions', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Permissions.CanCreate

    # Test get permissions of no user authenticated.
    def test_notoken_perms(self):
        db.session.add(self.test_committee)
        db.session.commit()

        user_data = {
            "id": self.test_committee.id
        }
        self.socketio.emit('get_permissions', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Permissions.CanView

    # Test get permissions of committee member.
    def test_member_perms(self):
        db.session.add(self.test_committee)
        db.session.commit()

        testcomm = Committees(id="testcomm")
        testcomm.title = "TestComm"

        db.session.add(testcomm)
        db.session.commit()

        membership = Members(role= Roles.NormalMember)
        membership.member = self.test_user
        testcomm.members.append(membership)

        user_data = {
            "token": self.user_token,
            "id": "testcomm",
        }

        self.socketio.emit('get_permissions', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Permissions.CanContribute

    # Test get permissions fail.
    def test_noexistent_perms(self):
        db.session.add(self.test_committee)
        db.session.commit()

        user_data = {
            "id": "nonexistentcommittee"
        }
        self.socketio.emit('get_permissions', user_data)
        received = self.socketio.get_received()
        assert received[0]["args"][0] == Response.ComDoesntExist
