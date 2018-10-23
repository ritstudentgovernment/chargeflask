"""
filename: controllers.py
description: Controller for notes.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/02/18
"""

from flask_socketio import emit
from app.check_data_type import ensure_dict, authenticated_only
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
@socketio.on('create_note')
@ensure_dict
@authenticated_only
def create_note(user, user_data):

    action = Actions.query.filter_by(id= user_data.get('action',-1)).first()

    if user is None:
        emit("create_note", Response.UsrDoesntExist)
        return;

    if action is None:
        emit("create_note", Response.ActionDoesntExist)
        return;

    charge = Charges.query.filter_by(id= action.charge).first()
    committee = Committees.query.filter_by(id= charge.committee).first()

    if (not user.is_admin and 
        committee.head != user.id and 
        committee not in user.committees):
        emit("create_note", Response.UsrNotAuth)
        return;

    note = Notes()
    note.action = action.id
    note.description = user_data.get('description',"")
    note.status = user_data.get('status',0)
    note.author = user.id
    note.hidden = False
    db.session.add(note)

    try:
        db.session.commit()
        emit('create_note', Response.AddSuccess)
        get_notes(action.id, broadcast = True)
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        emit("create_note", Response.AddError)
    

##
## @brief      Gets notes from an action
##
## @param      action_id    - id of the action
##
@socketio.on('get_notes')
def get_notes(action_id, broadcast = False):
    notes = Notes.query.filter_by(action= action_id).all()
    note_ser = [
                    {
                        "id": c.id,
                        "author": "{} {}".format(Users.query.filter_by(id = c.author).first().first_name, Users.query.filter_by(id = c.author).first().last_name),
                        "action": c.action,
                        "description": c.description,
                        "status": c.status,
                        "action": c.action,
                        "created_at": c.created_at.isoformat(),
                        "hidden": c.hidden
                    }
                    for c in notes
                ]
    emit("get_notes", note_ser, broadcast = broadcast)

##
## @brief      Gets a note
##
## @param      id       - id of the note
##
@socketio.on('get_note')
def get_note(id, broadcast = False):

    note = Notes.query.filter_by(id= id).first()
    if note is not None:
        note_data = {
            "id": note.id,
            "author": note.author,
            "action": note.action,
            "description": note.description,
            "created_at": note.created_at,
            "hidden": note.hidden
        }
        emit('get_note', note_data, broadcast = broadcast)
    else:
        emit("get_note", {}, broadcast = broadcast)

##
## @brief      Edits a note (Must be admin user or committe head to hide,
##              only author can edit the description)
##
## @param      user_data  The user data to edit a note, must
##                        contain a token, an id and any of the following
##                        fields:
##                        - description
##                        - hidden
##
##                        Any other field will be ignored.
##
## @emit       Emits a success mesage if edited, errors otherwise.
##

@socketio.on('modify_note')
@ensure_dict
@authenticated_only
def modify_note(user, user_data):

    if(user is None):
        emit('modify_note', Response.UsrDoesntExist)
        return
    note = Notes.query.filter_by(id= user_data.get('id',-1)).first()

    if(note is None):
        emit('modify_note', Response.NoteDoesntExist)
        return

    action = Actions.query.filter_by(id= note.action).first()
    charge = Charges.query.filter_by(id= action.charge).first()
    committee = Committees.query.filter_by(id= charge.committee).first()

    if(user.id == note.author):

        if "description" in user_data:
            note.description = user_data['description']

    if(user.id == committee.head or user.is_admin or user.id == note.author):

        if "hidden" in user_data:
            note.hidden = user_data['hidden']

        db.session.add(note)

        try:
            db.session.commit()
            emit('modify_note', Response.ModifySuccess)
            get_note(note.id, broadcast = True)
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            emit("modify_note", Response.ModifyError)
    else:
        emit("modify_note", Response.UsrNotAuth)
