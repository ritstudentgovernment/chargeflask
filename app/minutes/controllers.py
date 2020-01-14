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
from app.minutes.models import Minutes
from app.charges.models import Charges
from app.minutes.minutes_response import Response
from app.users.models import Users


##
## @brief      Gets a minute object.
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - minute_id (Integer)   the id of the minute.
##
## @emit       returns a valid minute.
##
@socketio.on('get_minute')
@ensure_dict
@get_user
def get_minute(user, user_data):
    minute = Minutes.query.filter_by(id= user_data.get("minute_id", -1)).first()
    
    if user is None:
        emit('get_minute', Response.UserDoesntExist)
        return

    if minute is None:
        emit('get_minute', Response.MinuteDoesntExist)
        return
    
    committee = minute.committee 

    membership = committee.members.filter_by(member = user).first()

    if minute.private and (membership is None and not user.is_admin and committee.head != user.id):
        emit('get_minute', Response.PermError)
        return
    
    minute_data = {
        'id': minute.id,
        'title': minute.title,
        'body': minute.body,
        'date': minute.date,
        'private': minute.private,
        'committee_id': minute.committee_id,
        'charges': [{"id": c.id, "title": c.title} for c in minute.charges]
    }
    emit('get_minute', minute_data)


##
## @brief      Gets an array of minutes
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - committee_id (Integer)   the id of the committee.
##
## @emit       Emits a list of minutes
##
@socketio.on('get_minutes')
@ensure_dict
@get_user
def get_minutes(user, user_data):
    committee = Committees.query.filter_by(id = user_data.get("committee_id","")).first()

    if user is None:
        emit('get_minutes', Response.UserDoesntExist)
        return
    
    if committee is None:
        emit('get_minutes', Response.CommitteeDoesntExist)
        return
    
    # Get the members role.
    membership = committee.members.filter_by(member= user).first()
    minutes = None

    if (membership is None and not user.is_admin and committee.head != user.id):
        minutes = committee.minutes.filter_by(private= False).all()
    else:
        minutes = committee.minutes.all()
    
    minute_data = []
    
    for minute in minutes:
        minute_data.append({
            'id': minute.id,
            'title': minute.title,
            'body': minute.body,
            'private': minute.private,
            'date': minute.date,
            'committee_id': minute.committee_id,
            'charges': [{"id": c.id, "title": c.title} for c in minute.charges]
        })
    emit('get_minutes', minute_data)


##
## @brief      Creates a new minute
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - committee_id (Integer)   the id of the committee.
##             - title (String)           the title of the minute
##             - body (String)            the text of the minute.
##             - date (Integer)           Epoch date of minute creation.
##             - private (Boolean)        True if minute is private.
##             - charges ([String])       (optional) A list of charge_ids.
##
## @emit       Emits a AddMinuteSuccess on minute creation.
##
@socketio.on('create_minute')
@ensure_dict
@get_user
def create_minute(user, user_data):
    committee =  Committees.query.filter_by(id = user_data.get("committee_id","")).first()

    if user is None:
        emit('create_minute', Response.UserDoesntExist)
        return
    
    if committee is None:
        emit('create_minute', Response.CommitteeDoesntExist)
        return
    
    if (user_data.get("title","") == "" or
        user_data.get("body","") == "" or 
        user_data.get("date","") == ""):
        emit('create_minute', Response.AddMinuteError)
        return

    # Get the members role.
    membership = committee.members.filter_by(member= user).first()

    if (user.id != committee.head and user.is_admin == False and
        (membership is None or membership.role != Roles.MinuteTaker)):
        emit('create_minute', Response.PermError)
        return
    
    if user.id != committee.head and not user_data["private"]:
        emit('create_minute', Response.PermError)
        return
    
    minute = Minutes(title= user_data["title"])
    minute.body = user_data["body"]
    minute.date = int(user_data["date"])
    minute.private = user_data["private"]
    minute.committee = committee

    if "charges" in user_data:
        for charge_id in user_data["charges"]:
            charge = Charges.query.filter_by(id = charge_id).first()
            minute.charges.append(charge)
    
    try:
        db.session.add(minute)
        db.session.commit()
        emit('create_minute', Response.AddMinuteSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit("create_minute", Response.AddMinuteError)


## @brief      Deletes a Minute
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - minute_id (Integer) The id of the minute to delete.
##
## @emit       Emits DeleteMinuteSuccess on deletion.
##
@socketio.on('delete_minute')
@ensure_dict
@get_user
def delete_minute(user, user_data):
    minute = Minutes.query.filter_by(id = user_data.get("minute_id",-1)).first()

    if user is None:
        emit('delete_minute', Response.UserDoesntExist)
        return

    if minute is None:
        emit('delete_minute', Response.MinuteDoesntExist)
        return
    
    if user.id != minute.committee.head and not user.is_admin:
        emit('delete_minute', Response.PermError)
        return

    try:
        db.session.delete(minute)
        emit('delete_minute', Response.DeleteMinuteSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit('delete_minute', Response.DeleteMinuteError)


## @brief      Edits a minute
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - minute_id (Integer)   the id of the minute.
##
## @emit       Emits - Updates given minute on success
##

@socketio.on('edit_minute')
@ensure_dict
@get_user
def edit_minute(user, user_data):
    minute = Minutes.query.filter_by(id= user_data.get("minute_id", -1)).first()

    if user is None:
        emit('edit_minute', Response.UserDoesntExist)
        return

    if minute is None:
        emit('edit_minute', Response.MinuteDoesntExist)
        return
    
    committee = minute.committee 

    membership = committee.members.filter_by(member= user).first()

    if (user.id != committee.head and user.is_admin == False and
        (membership is None or membership.role != Roles.MinuteTaker)):
        emit('edit_minute', Response.PermError)
        return
    
    if (user.id != committee.head and 
        "private" in user_data and not user_data["private"]):
        emit('create_minute', Response.PermError)
        return
    
    deleted = []
    new = []

    if "charges" in user_data:
        existing = set([x.id for x in minute.charges])
        deleted = list(existing - set(user_data["charges"]))
        new = list(set(user_data["charges"]) - existing)
    
    deleted = [i for i, j in zip(minute.charges, deleted) if i.id == j]

    q = db.session.query(Charges)
    new = q.filter(Charges.id.in_(new)).all()

    for key in user_data:
        if(key =="title" or key == "body" or key == "private"):
            setattr(minute, key, user_data[key])
    
    try:
        for charge in new:
            minute.charges.append(charge)
        
        for charge in deleted:
            minute.charges.remove(charge)
        
        db.session.commit()
        emit('edit_minute', Response.EditSuccess)
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        emit("edit_minute", Response.EditError)
