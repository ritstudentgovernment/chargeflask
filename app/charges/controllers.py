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
## @return     All charges.
##
@socketio.on('get_all_charges')
def get_all_charges(broadcast = False):

    charges = Charges.query.filter_by().all()
    charge_ser = []

    for charge in charges:
        if charge.private:
            continue;

        charge_ser.append({
            "id": charge.id,
            "title": charge.title,
            "description": charge.description,
            "committee": charge.committee,
            "priority": charge.priority,
            "status": charge.status,
            "paw_links": charge.paw_links,
            "created_at": charge.created_at.isoformat()
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
    charges = Charges.query.filter_by(committee= user_data.get("committee_id", "")).all()
    charge_ser = []

    if len(charges) == 0:
        emit("get_charges", charge_ser, broadcast = broadcast)
        return;

    committee = Committees.query.filter_by(id = user_data.get("committee_id", "")).first()
    membership = committee.members.filter_by(member= user).first()

    for charge in charges:
        if charge.private and membership is None:
            continue;

        charge_ser.append({
            "id": charge.id,
            "title": charge.title,
            "description": charge.description,
            "committee": charge.committee,
            "priority": charge.priority,
            "status": charge.status,
            "paw_links": charge.paw_links,
            "private": charge.private,
            "created_at": charge.created_at.isoformat()
        });
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

    charge = Charges.query.filter_by(id= user_data["charge"]).first()

    if charge is None:
        emit('get_charge', Response.UsrChargeDontExist)
        return;

    committee = Committees.query.filter_by(id = charge.committee).first()
    membership = committee.members.filter_by(member= user).first()

    if charge.private and (membership is None and not user.is_admin):
        emit('get_charge', Response.PermError)
        return;

    charge_info = {
        "id": charge.id,
        "title": charge.title,
        "description": charge.description,
        "committee": charge.committee,
        "priority": charge.priority,
        "status": charge.status,
        "paw_links": charge.paw_links,
        "private": charge.private,
        "created_at": charge.created_at.isoformat()
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

    if committee is None or user is None:
        emit("create_charge", Response.UsrChargeDontExist)
        return;

    # Get the members role.
    membership = committee.members.filter_by(member= user).first()

    if (user.id != committee.head and user.is_admin == False):
        emit("create_charge", Response.PermError)
        return;

    if "title" not in user_data:
        emit ("create_charge", Response.InvalidTitle)
        return;

    if ("priority" not in user_data or
        type(user_data["priority"]) != int or 
        user_data["priority"] < 0 or
        user_data["priority"] > 2):
        emit ("create_charge", Response.InvalidPriority)
        return;

    # Only admins and committee heads can make charges public.
    if ('private' in user_data and not user_data['private'] and
        not user.is_admin and user.id != committee.head):
        emit("create_charge", Response.PermError)
        return;

    charge = Charges(title = user_data["title"])
    charge.author = user.id
    charge.description = user_data.get("description", "")
    charge.committee = committee.id
    charge.status = int(user_data.get("status", ""))
    charge.priority = 0
    charge.objectives = user_data.get("objectives", [])
    charge.schedule = user_data.get("schedules", [])
    charge.resources = user_data.get("resources", [])
    charge.stakeholders = user_data.get("stakeholders", [])
    charge.paw_links = user_data.get("paw_links", "")
    charge.private = user_data.get("private", True)

    db.session.add(charge)

    try:
        db.session.commit()
        emit('create_charge', Response.AddSuccess)
        get_charges(user_data, broadcast= True)
    except Exception as e:
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

    if charge is None or user is None:
        emit('edit_charge', Response.UsrChargeDontExist)
        return

    committee = Committees.query.filter_by(id = charge.committee).first()
    membership = committee.members.filter_by(member= user).first()

    if (user.id != committee.head and user.is_admin == False and
        (membership is None or membership.role != Roles.ActiveMember)):
        emit("edit_charge", Response.PermError)
        return

    # Only admins and committee heads can make charges public.
    if ('private' in user_data and not user_data['private'] and
        not user.is_admin and user.id != committee.head):
        emit("edit_charge", Response.PermError)
        return
    
    # Only admins can move charges to a different committee.
    if ('committee' in user_data and user.is_admin == False):
        emit("edit_charge", Response.PermError)
        return

    for key in user_data:
        if (key == "description" or key == "title" or key == "priority" or
            key == "status" or key == "paw_links" or key == "private" or key == "committee"):
            setattr(charge, key, user_data[key])

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
