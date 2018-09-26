"""
filename: controllers.py
description: Controllers for Memberships.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/26/17
"""

from flask_socketio import emit
from app.check_data_type import ensure_dict
from app import socketio, db
from app.committees.models import Committees
from app.users.models import Users
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
		mem_arr = [{"id": m.id} for m in members]
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
##                        - token (required): Token of current user.
##                        - user_id (optional): Id of user to be added, if not
##                          specified, current user will be added to committee.
##                        - committee_id (required): Id of committee.
##
##                        Any other parameters will be ignored.
##
## @emit     Success if user could be added to committee, error if not.
##
@socketio.on('add_member_committee')
@ensure_dict
def add_to_committee(user_data):
	print("here enter")

	user = Users.verify_auth(user_data.get("token",""))
	committee = Committees.query.filter_by(id= user_data.get("committee_id",-1)).first()

	new_user_id = user_data.get("user_id","")
	new_user = Users.query.filter_by(id= new_user_id).first()

	if committee is not None and new_user is not None and user is not None:

		if committee.head == user.id or user.is_admin:

			try:

				committee.members.append(new_user)
				get_committee_members(committee.id, broadcast = True)
				emit("add_member_committee", Response.AddSuccess)
			except Exception as e:

				db.session.rollback()
				emit("add_member_committee", Response.AddError)
		else:

			# Send request to join.
			request_result = send_request(new_user, committee)
			emit("add_member_committee", request_result)
	elif committee is not None and user is not None:
		print("here b")

		# Send invitation to join.
		invite_result = send_invite(new_user_id, committee)
		emit("add_member_committee", invite_result)
	else:
		emit("add_member_committee", Response.UserDoesntExist)


##
## @brief      Removes a member from a committee.
##
## @param      user_data  Contains the data needed to add a member to a committee.
##                        This can contain:
##
##                        - token (required): Token of current user.
##                        - user_id (required): Id of user to be deleted.
##                        - committee_id (required): Id of committee.
##
##                        Any other parameters will be ignored.
##
## @emit       Success if member could be deleted, error if not.
##
@socketio.on('remove_member_committee')
@ensure_dict
def remove_from_committee(user_data):

	user = Users.verify_auth(user_data.get("token",""))
	committee = Committees.query.filter_by(id= user_data.get("committee_id",-1)).first()
	delete_user = Users.query.filter_by(id= user_data.get("user_id","")).first()
	if committee is not None and delete_user is not None:

		if committee.head == user.id or user.is_admin:

			try:

				committee.members.remove(delete_user)
				get_committee_members(committee.id, broadcast = True)
				emit("remove_member_committee", Response.RemoveSuccess)
			except Exception as e:

				db.session.rollback()
				emit("remove_member_committee", Response.RemoveError)
		else:

			emit("remove_member_committee", Response.PermError)
	else:
		emit("remove_member_committee", Response.UserDoesntExist)
