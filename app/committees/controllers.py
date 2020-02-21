"""
filename: controllers.py
description: Controller for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/19/17
"""

from flask_socketio import emit
from app.decorators import ensure_dict, get_user
from app import socketio, db
from app.committees.committees_response import Response
from app.committees.models import Committees
from app.users.models import Users
from app.members.models import Members, Roles
from app.users.permissions import Permissions
import base64


##
## @brief      Gets list of all committees.
##
## @param      broadcast  Flag to broadcast list of committees to all users.
##
## @emit       Emits a list of committees.
##
@socketio.on('get_committees')
def get_committees(broadcast = False):
    committees = Committees.query.filter_by().all()
    comm_ser = [{"id": c.id, "title": c.title, "enabled": c.enabled} for c in committees]
    emit("get_committees", comm_ser, broadcast= broadcast)


##
## @brief      Get a users permissions for a specific committee.
##
## @param      user_data  Contains user "token" (optional) and
##                        "id" of committee. (required.)
##
## @emit       Integer describing the user permissions.
##
@socketio.on('get_permissions')
@ensure_dict
@get_user
def get_permissions(user, user_data):
    
    committee = Committees.query.filter_by(id = user_data.get("id",-1)).first()
    permission_level = Permissions.CanView

    if committee is not None:

        if user is not None:

            if user.is_admin:

                permission_level = Permissions.CanEdit
            elif user.id == committee.head:

                permission_level = Permissions.CanCreate
            elif committee.members.filter_by(member= user).first():

                permission_level = Permissions.CanContribute
        emit('get_permissions', permission_level)
    else:
        emit('get_permissions', Response.ComDoesntExist)


##
## @brief      Gets a specific committee by its id.
##
## @param      committee_id  The committee identifier
##
## @emit       An object containing a detailed view of a specific
##             committee.
##
@socketio.on('get_committee')
def get_committee(committee_id, broadcast = False):

    committee = Committees.query.filter_by(id = committee_id).first()

    if committee is not None:

        head = Users.query.filter_by(id = committee.head).first()

        committee_info = {
            "id": committee.id,
            "title": committee.title,
            "description": committee.description,
            "location": committee.location,
            "meeting_time": committee.meeting_time,
            "meeting_day": committee.meeting_day,
            "head": committee.head,
            "head_name": head.first_name + " " + head.last_name
        }

        if committee.committee_img is not None:
            com_img = base64.b64encode(committee.committee_img).decode('utf-8')
            committee_info["committee_img"] = com_img

        emit("get_committee", committee_info, broadcast= broadcast)
    else:
        emit('get_committee', Response.ComDoesntExist)


##
## @brief      Creates a committee. (Must be admin user)
##
## @param      user_data  The user data required to create a committee.
##
##                        All the following fields are required:
##
##                        token - Token of the current user
##                        title - The title of the new committee
##                        head - Head of committee (Must exist in app)
##                        description - Description of new committee
##                        location - Location of committee meetings
##                        meeting_time - Time of committee meeting
##                        meeting_day - Day of the week of committee meeting
##
## @emit       Emits a success message if created, error if not.
##
@socketio.on('create_committee')
@ensure_dict
@get_user
def create_committee(user, user_data):
    
    if user is not None and user.is_admin:

        # Build committee id string.
        committee_id = user_data["title"].replace(" ", "")
        committee_id = committee_id.lower()

        if Committees.query.filter_by(id = committee_id).first() is None:

            if ("title" in user_data and
                "description" in user_data and
                "location" in user_data and
                "meeting_time" in user_data and
                "meeting_day" in user_data and
                "head" in user_data):

                new_committee = Committees(id = committee_id)
                new_committee.title = user_data["title"]
                new_committee.description = user_data["description"]
                new_committee.location = user_data["location"]
                new_committee.meeting_time = user_data["meeting_time"]
                new_committee.meeting_day = user_data["meeting_day"]
                
                new_committee.head = user_data["head"]
                membership = Members(role= Roles.CommitteeHead)
                membership.member = Users.query.filter_by(id= user_data["head"]).first()
                new_committee.members.append(membership)

                if "committee_img" in user_data:
                    com_img = base64.b64decode(user_data["committee_img"])
                    new_committee.committee_img = com_img
                
                db.session.add(new_committee)
                try:

                    db.session.commit()
                    emit('create_committee', Response.AddSuccess)
                    get_committees(broadcast= True)
                except Exception as e:

                    db.session.rollback()
                    db.session.flush()
                    emit("create_committee", Response.AddError)
            else:
                emit('create_committee', Response.AddError)
        else:
            emit('create_committee', Response.AddExists)
    else:
        emit('create_committee', Response.UsrDoesntExist)


##
## @brief      Edits a committee (Must be admin user)
##
## @param      user_data  The user data to edit a committee, must
##                        contain a token and any of the following
##                        fields:
##                        - description
##                        - head
##                        - location
##                        - meeting_time
##                        - enabled
##                        - committee_img
##
##                        Any other field will be ignored.
##
## @emit       Emits a success mesage if edited, errors otherwise.
##
@socketio.on('edit_committee')
@ensure_dict
@get_user
def edit_committee(user, user_data):

    if user is None or not user.is_admin:
        emit('edit_committee', Response.UsrDoesntExist)
        return;
 
    committee = Committees.query.filter_by(id= user_data.get("id")).first()

    if committee is None:
        emit('edit_committee', Response.ComDoesntExist)
        return;
    
    for key in user_data:

        if (key == "description" or key == "location" or
            key == "meeting_time" or key == "enabled" or key == "committee_img"):
            
            if key == "committee_img":

                com_img = base64.b64decode(user_data["committee_img"])
                setattr(committee, key, com_img)
            else:
                setattr(committee, key, user_data[key])

    try:

        if "head" in user_data and committee.head != user_data["head"]:
            new_head = Users.query.filter_by(id = user_data["head"]).first()

            if new_head is None:
                emit("edit_committee", Response.UsrDoesntExist)
                return
            
            membership = committee.members.filter_by(users_id= committee.head).first()
            membership.member = new_head
            committee.head = new_head.id

        db.session.commit()
    
        # Send successful edit notification to user
        # and broadcast committee changes.
        emit("edit_committee", Response.EditSuccess)
        get_committee(committee.id, broadcast= True)
        get_committees(broadcast= True)
    except Exception as e:
        db.session.rollback()
        emit("edit_committee", Response.EditError)
