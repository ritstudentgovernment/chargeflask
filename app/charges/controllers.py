"""
filename: controllers.py
description: Cronrollers for charges.
created by: Omar De La Hoz (oed7416@rit.edu), Chris Lemelin (cxl8826@rit.edu)
created on: 12/05/17
"""

from flask_socketio import emit
from app.check_data_type import ensure_dict
from app import socketio, db
from app.charges.models import *
from app.committees.models import Committees
from app.charges.charges_response import Response
from app.users.models import Users


##
## @brief      Gets the charges for a specific committee.
##
## @param      committee_id  The committee identifier
## @param      broadcast     Flag to broadcast list of charges
##                           to all users.
##
## @emit       Emits a list of charges for committee.
##


@socketio.on('get_all_charges')
def get_all_charges(committee_id, broadcast = False):
    charges = Charges.query.filter_by().all()
    charge_ser = [
                    {
                        "id": charge.id,
                        "title": charge.title,
                        "description": charge.description,
                        "committee": charge.committee,
                        "priority": charge.priority,
                        "status": charge.status
                    }
                    for charge in charges
                ]
    emit("get_all_charges", charge_ser, broadcast = broadcast)



@socketio.on('get_charges')
def get_charges(committee_id, broadcast = False):
    charges = Charges.query.filter_by(committee= committee_id).all()
    charge_ser = [
                    {
                        "id": charge.id,
                        "title": charge.title,
                        "description": charge.description,
                        "committee": charge.committee,
                        "priority": charge.priority,
                        "status": charge.status
                    }
                    for charge in charges
                ]
    emit("get_charges", charge_ser, broadcast = broadcast)


##
## @brief      Gets a charge by its ID.
##
## @param      charge_id  The charge identifier
## @param      broadcast  Flag to broadcast list of charges
##                        to all users.
##
## @emit       An objet containing the detailed view of a
##             charge.
##
@socketio.on('get_charge')
def get_charge(charge_id, broadcast = False):

    charge = Charges.query.filter_by(id= charge_id).first()

    if charge is None:
        emit('get_charge', Response.UsrChargeDontExist)
        return;

    charge_info = {
        "id": charge.id,
        "title": charge.title,
        "description": charge.description,
        "committee": charge.committee,
        "priority": charge.priority,
        "status": charge.status,
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
##             - priority (required): The charge's priority.
##             - description: The purpose of the charge.
##             - objectives: The objectives of a charge (Array).
##
##
## @return     { description_of_the_return_value }
##
@socketio.on('create_charge')
@ensure_dict
def create_charge(user_data):
    user = Users.verify_auth(user_data.get("token",""))
    committee = Committees.query.filter_by(id = user_data.get("committee","")).first()

    if committee is None or user is None:
        emit("create_charge", Response.UsrChargeDontExist)
        return;

    if user.id != committee.head and user.is_admin == False:
        emit("create_charge", Response.UsrChargeDontExist)
        return;

    if "title" not in user_data:
        emit ("create_charge", Response.InvalidTitle)
        return;

    if ("priority" not in user_data or
        user_data["priority"] < 0 or
        user_data["priority"] > 2):
        emit ("create_charge", Response.InvalidPriority)
        return;

    charge = Charges(title = user_data["title"])
    charge.author = user.id
    charge.description = user_data.get("description", "")
    charge.committee = committee.id
    charge.status = 0
    charge.priority = 0
    charge.objectives = user_data.get("objectives", [])
    charge.schedule = user_data.get("schedules", [])
    charge.resources = user_data.get("resources", [])
    charge.stakeholders = user_data.get("stakeholders", [])

    db.session.add(charge)

    try:
        db.session.commit()
        emit('create_charge', Response.AddSuccess)
        get_charges(committee.id, broadcast= True)
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
##
## @return     { description_of_the_return_value }
##
@socketio.on('edit_charge')
@ensure_dict
def edit_charge(user_data):
    user = Users.verify_auth(user_data.get("token",""))
    charge = Charges.query.filter_by(id = user_data.get("charge",-1)).first()

    if charge is not None and user is not None:
        committee = Committees.query.filter_by(id = charge.committee).first()

        if (committee.head == user.id or user.is_admin):

            for key in user_data:
                if (key == "description" or key == "title" or key == "priority" or
                    key == "status"):
                    setattr(charge, key, user_data[key])

            try:
                db.session.commit()
                # Send successful edit notification to user
                # and broadcast charge changes.
                emit("edit_charge", Response.EditSuccess)

                get_charge(charge.id, broadcast= True)
                get_charges(charge.committee, broadcast= True)

            except Exception as e:
                db.session.rollback()
                emit("edit_charge", Response.EditError)
        else:
            emit('edit_charge', Response.EditError)
    else:
        emit('edit_charge', Response.UsrChargeDontExist)
