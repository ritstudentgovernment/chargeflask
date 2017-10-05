"""
filename: controllers.py
description: Controllers for Memberships.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/26/17
"""

from flask_socketio import emit
from app import socketio, db
from app.committees.models import Committees
from app.users.models import Users


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
		emit("get_members", {"error": "Committee doesn't exist."})


##
## @brief      Adds to committee.
##
## @param      user_data  The user data
##
## @emit     Success if user could be added to committee, error if not.
##
@socketio.on('add_member_committee')
def add_to_committee(user_data):

	user = Users.verify_auth(user_data["token"])
	committee = Committees.query.filter_by(id= user_data["committee_id"]).first()

	new_user_id = user_data["user_id"] if "user_id" in user_data else user.id
	new_user = Users.query.filter_by(id= new_user_id).first()

	if committee is not None and new_user is not None:

		if committee.head == user.id or user.is_admin:

			try:
				
				committee.members.append(new_user)
				get_committee_members(committee.id, broadcast = True)
				emit("add_member_committee", {"success": "User has been added to committee"})
			except Exception as e:

				db.session.rollback()
				emit("add_member_committee", {"error": "User couldn't be added to committee"})
		else:

			# Send request to join.
			emit("add_member_committee", {"success": "Request to join has been sent"})
	else:
		emit("add_member_committee", {"error": "User or committee don't exist."})


##
## @brief      Removes a member from a committee.
##
## @param      user_data  The user data
##
## @emit       Success if member could be deleted, error if not.
##
@socketio.on('remove_member_committee')
def remove_from_committee(user_data):

	user = Users.verify_auth(user_data["token"])
	committee = Committees.query.filter_by(id= user_data["committee_id"]).first()
	delete_user = Users.query.filter_by(id= user_data["user_id"]).first()

	if committee is not None and delete_user is not None:

		if committee.head == user.id or user.is_admin:

			try:

				committee.members.remove(delete_user)
				get_committee_members(committee.id, broadcast = True)
				emit("remove_member_committee", {"success": "Member has been removed from committee"})
			except Exception as e:
				db.session.rollback()
				emit("remove_member_committee", {"error": "Member couldn't be removed from committee."})
		else:

			emit("remove_member_committee", {"error": "User doesn't have permissions to remove members."})
	else:
		emit("remove_member_committee", {"error": "User or committee don't exist."})
