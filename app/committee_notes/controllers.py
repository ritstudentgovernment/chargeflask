"""
filename: controllers.py
description: Controllers for committee notes.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/20/18
"""

from flask_socketio import emit
from app.decorators import ensure_dict
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
@ensure_dict
def create_note(user_data):
    user = Users.verify_auth(user_data.get("token", ""))
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

##
## @brief      Gets committee notes from a committee
##
## @param      committee_id     - id of the committee
##
@socketio.on('get_committee_notes')
def get_notes(committee_id, broadcast = False):
    notes = CommitteeNotes.query.filter_by(committee= committee_id).all()
    note_ser = [
                    {
                        "id": c.id,
                        "author": c.author,
                        "committee": c.committee,
                        "description": c.description,
                        "created_at": c.created_at,
                        "hidden": c.hidden
                    }
                    for c in notes
                ]
    emit("get_committee_notes", note_ser, broadcast = broadcast)

##
## @brief      Gets a committee note
##
## @param      id            - id of committee note.
##
@socketio.on('get_committee_note')
def get_note(id, broadcast = False):

    note = CommitteeNotes.query.filter_by(id= id).first()
    if note is not None:
        note_data = {
            "id": note.id,
            "author": note.author,
            "committee": note.committee,
            "description": note.description,
            "created_at": note.created_at,
            "hidden": note.hidden
        }
        emit('get_committee_note', note_data, broadcast = broadcast)
    else:
        emit("get_committee_note", {}, broadcast = broadcast)

##
## @brief      Edits a committee note (Must be admin user or committe head to hide,
##             only the author can edit the description)
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

@socketio.on('modify_committee_note')
@ensure_dict
def modify_note(user_data):

    user = Users.verify_auth(user_data.get("token",""))

    if(user is None):
        emit('modify_note', Response.UsrDoesntExist)
        return
    committee_note_id = user_data.get("id","")
    committee_note = CommitteeNotes.query.filter_by(id=committee_note_id).first()

    if(committee_note is None):
        emit('modify_note', Response.CommitteeNoteDoesntExist)
        return

    committee = Committees.query.filter_by(id= committee_note.committee).first()

    if(user.id == committee_note.author):

        if "description" in user_data:
            committee_note.description = user_data['description']

    if(user.id == committee.head or user.is_admin or user.id == committee_note.author):

        if "hidden" in user_data:
             committee_note.hidden = user_data['hidden']

        db.session.add(committee_note)

        try:
            db.session.commit()
            emit('modify_committee_note', Response.ModifySuccess)
            #get_note(committee_note.id, broadcast = True)
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            emit("modify_committee_note", Response.ModifyError)
    else:
        emit("modify_committee_note", Response.UsrNotAuth)
