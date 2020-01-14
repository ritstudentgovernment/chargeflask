"""
filename: controllers.py
description: Controllers for Memberships.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/26/17
"""

from flask_socketio import emit
from app.decorators import ensure_dict, get_user
from app import socketio, db
from app.committees.models import Committees
from app.users.models import Users
from app.members.models import Members, Roles
from app.members.members_response import Response
from app.invitations.controllers import send_invite, send_request


##
## @brief      Gets the committee members for a specific committee.
##
## @param      committee_id  The id for the committee.
##
## @emit       Array with committee members.
##
@socketio.on('get_members')
def get_committee_members(committee_id, broadcast= False):

    committee = Committees.query.filter_by(id= committee_id).first()

    if committee is not None:
        members = committee.members
        mem_arr = [
            {
                "id": m.member.id,
                "name": m.member.first_name + " " + m.member.last_name,
                "role": m.role.value
            } 
            for m in members
        ]
        mem_data = {"committee_id": committee.id, "members": mem_arr}
        emit("get_members", mem_data, broadcast= broadcast)
    else:
        emit("get_members", Response.ComDoesntExist)


##
## @brief      Adds to committee.
##
## @param      user_data  Contains the data needed to add a member to a committee.
##                        This can contain:
##
##                        - user_id (optional): Id of user to be added, if not
##                          specified, current user will be added to committee.
##                        - committee_id (required): Id of committee.
##                        - role (optional): Role of Member, if not defined it
##                                           will be set to NormalMember.
##
##                        Any other parameters will be ignored.
##
## @emit     Success if user could be added to committee, error if not.
##
@socketio.on('add_member_committee')
@ensure_dict
@get_user
def add_to_committee(user, user_data):

    committee = Committees.query.filter_by(id= user_data.get("committee_id",-1)).first()

    new_user_id = user_data.get("user_id","")
    new_user = Users.query.filter_by(id= new_user_id).first()

    # Committee and user are required, if None error out.
    if committee is None or user is None:
        emit("add_member_committee", Response.UserDoesntExist)
        return;

    # If user doesn't exist in app, invite him to join.
    if new_user is None:
        invite_result = send_invite(new_user_id, committee)
        emit("add_member_committee", invite_result)
        return;

    # If not head or admin, request to join committee.
    if committee.head != user.id and not user.is_admin:
        request_result = send_request(new_user, committee)
        emit("add_member_committee", request_result)
        return;

    # If user is head or admin and user exists in app,
    # add user to committee.
    try:
        membership = Members(role= Roles[user_data.get("role", Roles.NormalMember.value)])
        membership.member = new_user
        committee.members.append(membership)
        db.session.commit()

        get_committee_members(committee.id, broadcast = True)
        emit("add_member_committee", Response.AddSuccess)
    except Exception as e:
        db.session.rollback()
        emit("add_member_committee", Response.AddError)


##
## @brief      Removes a member from a committee.
##
## @param      user_data  Contains the data needed to remove a member from a committee.
##                        This can contain:
##
##                        - user_id (required): Id of user to be deleted.
##                        - committee_id (required): Id of committee.
##
##                        Any other parameters will be ignored.
##
## @emit       Success if member could be deleted, error if not.
##
@socketio.on('remove_member_committee')
@ensure_dict
@get_user
def remove_from_committee(user, user_data):

    committee = Committees.query.filter_by(id= user_data.get("committee_id",-1)).first()
    delete_user = Users.query.filter_by(id= user_data.get("user_id","")).first()

    if committee is None or delete_user is None:
        emit("remove_member_committee", Response.UserDoesntExist)
        return;

    if not committee.head == user.id or not user.is_admin:
        emit("remove_member_committee", Response.PermError)
        return;
    
    if committee.head == delete_user.id:
        emit("remove_member_committee", Response.RemoveHeadError)
        return;

    try:
        membership = committee.members.filter_by(member= delete_user).first()
        db.session.delete(membership)
        db.session.commit()
        get_committee_members(committee.id, broadcast = True)
        emit("remove_member_committee", Response.RemoveSuccess)
    except Exception as e:
        db.session.rollback()
        emit("remove_member_committee", Response.RemoveError)


##
## @brief      Edits the role of a committee member
##
## @param      user_data  Contains the data to edit a users role.
##                        This can contain:
##                        
##                        - user_id (required): Id of user to be deleted.
##                        - committee_id (required): Id of committee.
##                        - role (required): the users new role.
##
## @emit     Success if role was changed, error otherwise.
##
@socketio.on("edit_role_member_committee")
@ensure_dict
@get_user
def edit_member_role(user, user_data):

    committee = Committees.query.filter_by(id= user_data.get("committee_id",-1)).first()
    modify_user = Users.query.filter_by(id= user_data.get("user_id","")).first()

    try:
        role = Roles[user_data["role"]]
    except:
        emit("edit_role_member_committee", Response.RoleDoesntExist)
        return;

    if committee is None or modify_user is None:
        emit("edit_role_member_committee", Response.UserDoesntExist)
        return;

    if not committee.head == user.id or not user.is_admin:
        emit("edit_role_member_committee", Response.PermError)
        return;

    try:
        membership = committee.members.filter_by(member= modify_user).first()
        membership.role = role
        db.session.commit()
        emit("edit_role_member_committee", Response.EditSuccess)
    except Exception as e:
        db.session.rollback()
        emit("edit_role_member_committee", Response.EditError)
