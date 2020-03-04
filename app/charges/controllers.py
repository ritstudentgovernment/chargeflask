"""
filename: controllers.py
description: Cronrollers for charges.
created by: Omar De La Hoz (oed7416@rit.edu), Chris Lemelin (cxl8826@rit.edu)
created on: 12/05/17
"""

from flask_socketio import emit
from app.decorators import ensure_dict, get_user
from app import socketio, db
from app.charges.models import *
from app.committees.models import Committees
from app.members.models import Roles
from app.charges.charges_response import Response
from app.users.models import Users


##
## @brief      Gets all public charges.
##
## @param      broadcast  The broadcast
##
## @return     All public charges.
##
@socketio.on('get_all_charges')
def get_all_charges(broadcast = False):

    charges = Charges.query.filter_by(private = False).all()
    charge_ser = []

    for charge in charges:
        charge_ser.append({
            "id": charge.id,
            "title": charge.title,
            "description": charge.description,
            "committee": charge.committee,
            "priority": charge.priority,
            "status": charge.status,
            "paw_links": charge.paw_links,
            "created_at": charge.created_at.isoformat(),
            "progress_notes": charge.progress_notes
        });
    emit("get_all_charges", charge_ser, broadcast = broadcast)


##
## @brief      Gets the charges for a specific committee.
##
## @param      committee_id  The committee identifier
## @param      broadcast     Flag to broadcast list of charges
##                           to all users.
##
## @emit       Emits a list of charges for committee.
##
@socketio.on('get_charges')
@ensure_dict
@get_user
def get_charges(user, user_data, broadcast = False):   
    charge_ser = []
    committee_id = user_data.get("committee_id", "")
    committee = Committees.query.filter_by(id = committee_id).first()

    if committee is not None:
        membership = committee.members.filter_by(member= user).first()
        if (user is not None and user.is_admin) or membership is not None:
            charges = Charges.query.filter_by(committee= committee_id).all()
        else:
            charges = Charges.query.filter_by(committee= committee_id, private = False).all()

        for charge in charges:
            charge_ser.append({
                "id": charge.id,
                "title": charge.title,
                "description": charge.description,
                "committee": charge.committee,
                "priority": charge.priority,
                "status": charge.status,
                "paw_links": charge.paw_links,
                "private": charge.private,
                "created_at": charge.created_at.isoformat(),
                "progress_notes": charge.progress_notes
            })

    emit("get_charges", charge_ser, broadcast = broadcast)


##
## @brief      Gets a charge by its ID.
##
## @param      charge     The charge identifier
## @param      broadcast  Flag to broadcast list of charges
##                        to all users.
##
## @emit       An objet containing the detailed view of a
##             charge.
##
@socketio.on('get_charge')
@ensure_dict
@get_user
def get_charge(user, user_data, broadcast = False):
    charge_id = user_data.get("charge", -1)
    charge = Charges.query.filter_by(id= charge_id).first()

    if charge is None:
        emit('get_charge', Response.UsrChargeDontExist)
        return

    committee = Committees.query.filter_by(id = charge.committee).first()
    membership = committee.members.filter_by(member= user).first()

    if charge.private:
        if user is None or (not user.is_admin and membership is None):
            emit('get_charge', Response.PermError)
            return

    charge_info = {
        "id": charge.id,
        "title": charge.title,
        "description": charge.description,
        "committee": charge.committee,
        "priority": charge.priority,
        "status": charge.status,
        "paw_links": charge.paw_links,
        "private": charge.private,
        "created_at": charge.created_at.isoformat(),
        "progress_notes": charge.progress_notes
    }
    emit('get_charge', charge_info, broadcast= broadcast)


##
## @brief      Creates a charge for a Committee.
##
## A charge for a committee is created, the default
## status for the charge will be Unapproved, which
## means that the charge is a Charge Initiative.
##
## @param      user_data  The user data to create a
##             charge for a committee. This can include:
##
##             - token (required): Token of creator.
##             - title (required): Charge title.
##             - committee (required): The charge's committee.
##             - private (optional): Set charge to private or not,
##                                   only committee head and admins
##                                   can use them. If not defined,
##                                   private will be set to True.
##             - priority (required): The charge's priority.
##             - description: The purpose of the charge.
##             - objectives: The objectives of a charge (Array).
##
##
## @return     { description_of_the_return_value }
##
@socketio.on('create_charge')
@ensure_dict
@get_user
def create_charge(user, user_data):    
    committee = Committees.query.filter_by(id = user_data.get("committee","")).first()
    
    # The charge title must be at least 2 characters long and cannot contain special characters
    invalid_chars = r'/^()#@![]{}`~\?%*:|"<>.'
    titleNoneType = not user_data['title']
    titleTooShort = (len(user_data['title']) <= 1)
    titleInvalidChars = any(char in user_data['title'] for char in invalid_chars)

    if titleNoneType or titleTooShort or titleInvalidChars:
        emit('create_charge', Response.InvalidTitle)
        return

    if committee is None or user is None:
        emit("create_charge", Response.UsrChargeDontExist)
        return

    if (user.id != committee.head and not user.is_admin):
        emit("create_charge", Response.PermError)
        return

    if "title" not in user_data:
        emit ("create_charge", Response.InvalidTitle)
        return

    if ("priority" not in user_data or
        type(user_data["priority"]) != int or 
        user_data["priority"] < 0 or
        user_data["priority"] > 2):
        emit ("create_charge", Response.InvalidPriority)
        return

    charge = Charges(title = user_data["title"])
    charge.author = user.id
    charge.description = user_data.get("description", "")
    charge.committee = committee.id
    charge.status = user_data.get("status", "")
    charge.priority = 0
    charge.objectives = user_data.get("objectives", [])
    charge.schedule = user_data.get("schedules", [])
    charge.resources = user_data.get("resources", [])
    charge.stakeholders = user_data.get("stakeholders", [])
    charge.paw_links = user_data.get("paw_links", "")
    charge.private = user_data.get("private", True)
    charge.progress_notes = None # Charges have no progress notes initially

    db.session.add(charge)

    try:
        db.session.commit()
        emit('create_charge', Response.AddSuccess)
        get_charges(user_data, broadcast= True)
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        emit("create_charge", Response.AddError)

##
## @brief       edits a charge
##
## A charge for a committee is created, the default
## status for the charge will be Unapproved, which
## means that the charge is a Charge Initiative.
##
## This function contains the behavior to edit and delete progress_notes within a charge
##
## @param      user_data  The user data to create a
##             charge for a committee. This can include:
##
##             - token (required): Token of creator.
##             - charge (requred): charge to edit
##             - title : new title
##             - description : new description
##             - priority: new priority
##             - status: new status
##             - private (optional): Set charge to private or not,
##                                   only committee head and admins
##                                   can set privacy. If not defined,
##                                   private will be set to True.
##
## @return     { description_of_the_return_value }
##
@socketio.on('edit_charge')
@ensure_dict
@get_user
def edit_charge(user, user_data):
    charge = Charges.query.filter_by(id = user_data.get("charge",-1)).first()

    # The charge title must be at least 2 characters long and cannot contain special characters
    invalid_chars = r'/^()#@![]{}`~\?%*:|"<>.'
    titleNoneType = not user_data['title']
    titleTooShort = len(user_data['title']) <= 1
    titleInvalidChars = any(char in user_data['title'] for char in invalid_chars)

    if titleNoneType or titleTooShort or titleInvalidChars:
        emit('edit_charge', Response.InvalidTitle)
        return

    if charge is None or user is None:
        emit('edit_charge', Response.UsrChargeDontExist)
        return

    committee = Committees.query.filter_by(id = charge.committee).first()
    membership = committee.members.filter_by(member= user).first()

    if (membership is None or membership.role != Roles.CommitteeHead) and not user.is_admin:
        emit("edit_charge", Response.PermError)
        return
    
    # Only admins can move charges to a different committee.
    committee_id = user_data.get("committee", committee.id)
    if (committee_id != committee.id and not user.is_admin):
        emit("edit_charge", Response.PermError)
        return

    for key in user_data:
        if (key == "description" or key == "title" or key == "priority" or
            key == "status" or key == "paw_links" or key == "private" or key == "committee"):
            setattr(charge, key, user_data[key])

        # Edit progress notes
        if (key == "progress_notes"): 
            current_notes = getattr(charge, "progress_notes") 

            # Get the progress note info from user_data
            note_id = int(user_data["progress_notes"]["id"])
            note = str(user_data["progress_notes"]["note"])
            date = str(user_data["progress_notes"]["date"])

            # Edit the notes, and update the DB
            current_notes.edit(note_id, [note, date, str(note_id)])
            setattr(charge, "progress_notes", current_notes) 

        #Delete progress_notes
        if (key == "delete_note"): 
            current_notes = getattr(charge, "progress_notes") 

            note_id = int(user_data["delete_note"]["id"])

            current_notes.pop(note_id)
            setattr(charge, "progress_notes", current_notes)

    try:
        db.session.commit()
        # Send successful edit notification to user
        # and broadcast charge changes.
        emit("edit_charge", Response.EditSuccess)
        get_charge(user_data, broadcast= True)
        get_charges(user_data, broadcast= True)
    except Exception as e:
        db.session.rollback()
        emit("edit_charge", Response.EditError)

##
## @brief       Adds a progress note
##
## @param      user_data  The user data to create a
##             progress note for a charge:
##
##             - token (required): Token of creator.
##             - charge (requred): charge to add note to
##             - note : a string containing the progress note
##             - date : a string containing the date the note was made
##
## @return     { description_of_the_return_value }
##
@socketio.on('add_progress_note')
@ensure_dict
@get_user
def edit_charge(user, user_data):
    charge = Charges.query.filter_by(id = user_data.get("charge",-1)).first()

    if charge is None or user is None:
        emit('add_progress_note', Response.UsrChargeDontExist)
        return

    # Get the current list of notes
    current_notes = getattr(charge, "progress_notes")
    if (current_notes == None):
        current_notes = []

    # Create the new one from the user data
    new_note = []
    new_note.append(user_data.get("note"))
    new_note.append(user_data.get("date"))
    new_note.append(user_data.get("id"))

    # Add the new note to the current list of notes
    current_notes.append(new_note)
    
    # Overwrite the old list with the new one
    setattr(charge, "progress_notes", current_notes)

    try:
        db.session.commit()
        # Send successful edit notification to user
        # and broadcast charge changes.
        emit("edit_charge", Response.EditSuccess)
        get_charge(user_data, broadcast= True)
        get_charges(user_data, broadcast= True)
    except Exception as e:
        db.session.rollback()
        emit("edit_charge", Response.EditError)


##
## @brief       Delete a progress note
##
## @param      user_data  The user data to create a
##             progress note for a charge:
##
##             - token (required): Token of creator.
##             - charge (requred): charge to add note to
##             - id: an id used to index the progress note
##
## @return     { description_of_the_return_value }
##
@socketio.on('delete_progress_note')
@ensure_dict
@get_user
def edit_charge(user, user_data):
    print(user_data)
    charge = Charges.query.filter_by(id = user_data.get("charge",-1)).first()

    if charge is None or user is None:
        emit('add_progress_note', Response.UsrChargeDontExist)
        return

    # Get the current list of notes
    current_notes = getattr(charge, "progress_notes")
    if (current_notes == None):
        current_notes = []

    # Create the new one from the user data
    new_note = []
    new_note.append(user_data.get("note"))
    new_note.append(user_data.get("date"))
    new_note.append(user_data.get("id"))

    # Add the new note to the current list of notes
    current_notes.append(new_note)
    
    # Overwrite the old list with the new one
    setattr(charge, "progress_notes", current_notes)

    try:
        db.session.commit()
        # Send successful edit notification to user
        # and broadcast charge changes.
        emit("edit_charge", Response.EditSuccess)
        get_charge(user_data, broadcast= True)
        get_charges(user_data, broadcast= True)
    except Exception as e:
        db.session.rollback()
        emit("edit_charge", Response.EditError)

