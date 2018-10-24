"""
filename: controllers.py
description: Controller for action.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 03/23/18
"""

from flask_socketio import emit
from app.check_data_type import ensure_dict, get_user
from app import socketio, db
from app.actions.models import *
from app.charges.models import *
from app.committees.models import *
from app.actions.actions_response import Response
from app.users.models import Users

## @brief      Gets the actions for a specific charge.
##
## @param      charge_id     The charge identifier
## @param      broadcast     Flag to broadcast list of actions
##                           to all users.
##
## @emit       Emits a list of actions for charge.
##
@socketio.on('get_actions')
def get_actions(charge_id, broadcast = False):
    actions = Actions.query.filter_by(charge= charge_id).all()
    action_ser = [
                    {
                        "id": c.id,
                        "title": c.title,
                        "description": c.description,
                        "status": c.status,
                        "assigned_to": "{} {}".format(Users.query.filter_by(id = c.assigned_to).first().first_name, Users.query.filter_by(id = c.assigned_to).first().last_name),
                    }
                    for c in actions
                ]
    emit("get_actions", action_ser, broadcast = broadcast)


## @brief      Gets the action with a specific id
##
## @param      action_id     The action identifier
## @param      broadcast     Flag to broadcast list of actions
##                           to all users.
##
## @emit       Emits a list of actions for charge.
##
@socketio.on('get_action')
def get_action(action_id, broadcast = False):
    action = Actions.query.filter_by(id= action_id).first()

    if action is None:
        emit("get_action", Response.ActionDoesntExist)
        return


    action_info = {
        "id": action.id,
        "title": action.title,
        "description": action.description,
        "status": action.status
    }

    emit("get_action", action_info, broadcast = broadcast)

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
@ensure_dict
@get_user
def create_action(user, user_data):
    charge = Charges.query.filter_by(id = user_data.get("charge","")).first()
    assigned_to = Users.query.filter_by(id = user_data.get("assigned_to","")).first()

    if charge is None or user is None:
        emit("create_action", Response.UsrChargeDontExist)
        return

    committee = Committees.query.filter_by(id = charge.committee).first()
    
    if (committee not in user.committees and
        not user.is_admin and 
        committee.head != user.id):
        emit("create_action", Response.UsrNotAuth)
        return


    if (assigned_to is None or
        "title" not in user_data or
        "description" not in user_data):
        emit ("create_action", Response.AddError)
        return

    action = Actions(title = user_data["title"])
    action.author = user.id
    action.assigned_to = assigned_to.id
    action.description = user_data.get("description", "")
    action.charge = charge.id
    action.status = 0


    db.session.add(action)

    try:
        db.session.commit()
        emit('create_action', Response.AddSuccess)
        get_actions(charge.id, broadcast = True)
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        emit("create_action", Response.AddError)

##
## @brief      Edits an action (Must be the committee head or admin)
##
## @param      user_data  The user data to edit a committee, must
##                        contain a token and any of the following
##                        fields:
##                        - title
##                        - description
##                        - assigned_to
##                        - charge
##                        - status
##
##                        Any other field will be ignored.
##
##
@socketio.on('edit_action')
@ensure_dict
@get_user
def edit_action(user, user_data):
    action = Actions.query.filter_by(id = user_data.get("id","")).first()

    if action is None:
        emit('edit_action', Response.ActionDoesntExist)
        return

    charge = Charges.query.filter_by(id = action.charge).first()
    committee = Committees.query.filter_by(id = charge.committee).first()

    if not user.is_admin and not user.id == committee.head:
        emit('edit_action', Response.UsrNotAuth)
        return

    for key in user_data:

        if (key == "title" or key == "description" or key == "assigned_to" or
            key == "charge" or key == "status"):
            setattr(action, key, user_data[key])

    try:
        db.session.commit()

        # Send successful edit notification to user
        # and broadcast charge changes.
        emit("edit_action", Response.EditSuccess)
        get_actions(charge.id,broadcast= True)
    except Exception as e:
        db.session.rollback()
        emit("edit_action", Response.EditError)
