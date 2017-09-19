"""
filename: controllers.py
description: Controller for Committees.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/19/17
"""

from flask_socketio import emit
from app import socketio, db
from app.committees.models import Committees
from app.users.models import Users

##
## @brief      Gets list of all committees.
##
## @param      broadcast  Flag to broadcast list of committees to all users.
##
## @emit       Emits a list of committees and the committee count.
##
@socketio.on('get_committees')
def get_committees(broadcast = False):
	committees = Committees.query.all()
	comm_ser = [{"committee_id": c.id, "committee_title": c.title, "committee_description": c.description} for c in committees]
	emit("get_committees", {"committees": comm_ser, "count": len(committees)}, broadcast= broadcast)
	


##
## @brief      Gets a specific committee by its id.
##
## @param      committee_id  The committee identifier
##
## @emit       Committee Id, Title, Description and Committee Head.
##
@socketio.on('get_committee')
def get_committee(committee_id):

	committee = Committees.query.filter_by(id = committee_id).first()

	if committee is not None:

		emit("get_committee", {"committee_id": committee.id,
							   "committee_title": committee.title, 
							   "committee_description": committee.description,
							   "committee_head": committee.head})
	else:
		emit("error", "Committee doesn't exist.")


##
## @brief      Creates a committee.
##
## @param      user_data  The user data required to create a committee.
## 			   			  Contains keys 'token', 'committee_title', 
## 			   			  'committee_description' and 'head_id',
##
## @emit       Emits a success message if created, error if not.
##
@socketio.on('create_committee')
def create_committee(user_data):

	user = Users.verify_auth(user_data["token"])

	if user is not None and user.is_admin:

		new_committee = Committees(title= user_data["committee_title"])
		new_committee.description = user_data["committee_description"]
		new_committee.head = user_data["head_id"]

		db.session.add(new_committee)
		db.session.commit()
		emit('create_committee', 'Committee succesfully created')
		get_committees(broadcast= True)
