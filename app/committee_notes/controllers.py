"""
filename: controllers.py
description: Controllers for committee notes.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/20/18
"""

from flask_socketio import emit
from app import socketio, db
from app.committee_notes.models import *
from app.committees.models import *
from app.users.models import Users
from app.committee_notes.committee_notes_response import Response



##
## @brief      Creates a committee note. (Must be admin user or committe head)
##
## @param      user_data  The user data required to create a committee note
##
##                        All the following fields are required:
##                        committee         - id of the committee
##                        description       - Description of new committee note
##
@socketio.on('create_committee_note')
def create_note(user_data):

    user = Users.verify_auth(user_data["token"]) if "token" in user_data else None
    committe_id = user_data.get('committee', '')
    committee = Committees.query.filter_by(id=committe_id).first()

    if committee is not None:

        if(user is not None and (user.is_admin or committee.head == user.id)):
            committee_note = CommitteeNotes()
            committee_note.committee = committee.id
            committee_note.description = user_data.get('description',"")
            committee_note.author = user.id
            committee_note.hidden = False
            db.session.add(committee_note)

            try:
                db.session.commit()
                emit('create_committee_note', Response.AddSuccess)
                get_notes(action.id, broadcast = True)
            except Exception as e:
                db.session.rollback()
                db.session.flush()
                emit("create_committee_note", Response.AddError)
        else:
            emit("create_committee_note", Response.UsrNotAuth)
    else:
    	emit("create_committee_note", Response.CommitteeDoesntExist)
