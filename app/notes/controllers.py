"""
filename: controllers.py
description: Controller for notes.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/02/18
"""

from flask_socketio import emit
from app import socketio, db
from app.actions.models import *
from app.committees.models import *
from app.charges.models import *
from app.notes.models import *
from app.users.models import Users
from app.notes.notes_response import Response

##
## @brief      Creates a note. (Must be admin user or committe head or assigned to action)
##
## @param      user_data  The user data required to create a committee.
##
##                        All the following fields are required:
##                        action      - id of action
##                        description - Description of new note
##
## @emit       Emits a success message if created, error if not.
##
@socketio.on('create_note')
def create_note(user_data, broadcast= False):

    user = Users.verify_auth(user_data["token"]) if "token" in user_data else None
    action = Actions.query.filter_by(id= user_data['action']).first()

    if action is not None:
        charge = Charges.query.filter_by(id= action.charge).first()
        committee = Committees.query.filter_by(id= charge.committee).first()
        if(user is not None and (user.is_admin or committee.head == user.id)):
            note = Notes()
            note.action = action.id
            note.description = user_data['description']
            note.author = user.id
            db.session.add(note)

            try:
                db.session.commit()
                emit('create_note', Response.AddSuccess)
                #emit('get_actions', charge.id)
            except Exception as e:
                db.session.rollback()
                db.session.flush()
                emit("create_note", Response.AddError)
        else:
            emit("create_note", Response.UsrNotAuth)
    else:
    	emit("create_note", Response.ActionDoesntExist)
