"""
filename: controllers.py
description: Cronrollers for charges.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 12/05/17
"""

from flask_socketio import emit
from app import socketio, db
from app.charges.models import *
from app.committees.charges_response import Response
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
@socketio.on('get_charges')
def get_charges(committee_id, broadcast = False):
    charges = Charges.query.filter_by(committee= committee_id).all()
    charge_ser = [
                    {
                        "id": c.id,
                        "title": c.title,
                        "description": c.description
                    } 
                    for c in charges
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

    charge = Charges.query.filter_by(id= charge_id).all()

    if charge is None:
        emit('get_charge', "Charge doesn't exist.")
        return;

    charge_info = {
        "id": charge.id,
        "title": charge.title,
        "description": charge.description,
        "committee": "Commitee title",
        "committee_id": "ID",
        "priority": charge.priority
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
def create_charge(user_data):

    user = Users.verify_auth(user_data["token"]) if "token" in user_data else None
    committee = Committees.query.filter_by(id = user_data["committee"]).first()

    if committee is None or user is None:
        emit("create_charge", Response.UsrCommDontExist)
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
    charge.description = user_data["description"] if "description" in user_data else ""
    charge.committee = committee.id
    charge.status = StatusType.Unapproved
    charge.priority = user_data["priority"]

    db.session.add(charge)

    try:
        db.session.commit()
        emit('create_charge', Response.AddSuccess)
        get_charges(committee.id, broadcast= True)
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        emit("create_charge", Response.AddError)
