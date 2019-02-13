"""
filename: controllers.py
description: Controllers for Minutes.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 02/12/19
"""

from flask_socketio import emit
from app.decorators import ensure_dict, get_user
from app import socketio, db
from app.committees.models import Committees
from app.members.models import Roles
from app.minutes.models import Minutes, Topics
from app.minutes.minutes_response import Response
from app.users.models import Users

@socketio.on('create_minute')
@ensure_dict
@get_user
def create_minute(user, user_data):
    committee =  Committees.query.filter_by(id = user_data.get("committee","")).first()

    if committee is None or user is None:
        emit('create_minute', Response.UserDoesntExist)
        return
    
    if user_data["title"] is None or user_data["date"] is None:
        emit('create_minute', Response.AddError)
        return

    # Get the members role.
    membership = committee.members.filter_by(member= user).first()

    if (user.id != committee.head and user.is_admin == False and
        (membership is None or membership.role != Roles.MinuteTaker)):
        emit('create_minute', Response.PermError)
        return
    
    minute = Minutes(title= user_data["title"])
    minute.date = int(user_data["date"])

    if user_data["topics"]:
        for topic in user_data["topics"]:
            t_obj = Topics(topic= topic["topic"], body= topic["body"])
            minute.topics.append(t_obj)
    
    db.session.add(minute)

    try:
        db.session.commit()
        emit('create_minute', Response.AddSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit("create_minute", Response.AddError)
