"""
filename: controllers.py
description: Controller for action.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 03/23/18
"""

from flask_socketio import emit
from app import socketio, db
from app.actions.models import *
from app.charges.models import *
from app.committees.models import *
from app.actions.actions_response import Response
from app.users.models import Users


##
## @brief      Creates an action for a Charge.
##
## @param      user_data  The user data to create a
##             charge for a committee. This can include:
##
##             - token (required): Token of creator.
##             - title (required): the action's title.
##             - description (required): the action's description.
##             - assigned_to (required): who the action is assigned to.
##             - charge (required): action's charge
##
##
## @return     { description_of_the_return_value }
##
@socketio.on('create_action')
def create_action(user_data):
    user = Users.verify_auth(user_data["token"]) if "token" in user_data else None
    charge = Charges.query.filter_by(id = user_data["charge"]).first()
    assigned_to = Users.query.filter_by(id = user_data["assigned_to"]).first()

    if charge is None or user is None:
        emit("create_action", Response.UsrChargeDontExist)
        return

    committee = Committees.query.filter_by(id = charge.committee).first()

    if not user.is_admin and committee.head == user.id:
        emit("create_action", Response.UsrNotAuth)
        return


    if (assigned_to is None or
        "title" not in user_data or
        "description" not in user_data):
        emit ("create_action", Response.AddError)
        return

    action = Actions(title = user_data["title"])
    charge.author = user.id
    charge.description = user_data["description"]
    charge.charge = charge.id
    charge.status = ChargeStatusType.InProgress

    db.session.add(charge)

    try:
        db.session.commit()
        emit('create_action', Response.AddSuccess)
        # todo:
        # emit('get_actions', charge.id)
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        emit("create_action", Response.AddError)
