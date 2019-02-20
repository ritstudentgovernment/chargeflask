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
    committee =  Committees.query.filter_by(id = user_data.get("committee_id","")).first()

    if user is None:
        emit('create_minute', Response.UserDoesntExist)
        return
    
    if committee is None:
        emit('create_minute', Response.CommitteeDoesntExist)
        return
    
    if (user_data.get("title","") == "" or 
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
    minute.date = int(user_data["date"])

    if "topics" in user_data:
        for topic in user_data["topics"]:
            t_obj = Topics(topic= topic["topic"], body= topic["body"])
            minute.topics.append(t_obj)
    
    try:
        db.session.add(minute)
        db.session.commit()
        emit('create_minute', Response.AddMinuteSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit("create_minute", Response.AddMinuteError)


@socketio.on('create_minute_topics')
@ensure_dict
@get_user
def add_topics(user, user_data):
    minute = Minutes.query.filter_by(id = user_data.get("minute_id",-1)).first()

    if user is None:
        emit('create_minute_topics', Response.UserDoesntExist)
        return

    if minute is None:
        emit('create_minute_topics', Response.MinuteDoesntExist)
        return
    
    if "topics" not in user_data:
        emit('create_minute_topics', Response.InvalidData)
        return
    
    membership = minute.committee.members.filter_by(member= user).first()
    
    if (user.id != minute.committee.head and user.is_admin == False and
        (membership is None or membership.role != Roles.MinuteTaker)):
        emit('create_minute_topics', Response.PermError)
        return
    
    try:
        for topic in user_data["topics"]:
            t_obj = Topics(topic= topic["topic"], body= topic["body"])
            minute.topics.append(t_obj)
        
        db.session.commit()
        emit('create_minute_topics', Response.AddTopicSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit("create_minute_topics", Response.AddTopicError)


@socketio.on('delete_minute_topics')
@ensure_dict
@get_user
def remove_topics(user, user_data):

    if user is None:
        emit('delete_minute_topics', Response.UserDoesntExist)
        return
    
    if "topics" not in user_data:
        emit('delete_minute_topics', Response.InvalidData)
        return
    
    for topic in user_data["topics"]:
        
        topic_del = Topics.query.filter_by(id = user_data.get(topic.id,"")).first()
        
        if user.id != topic_del.minute.committee.head and user.is_admin == False:
            emit('delete_minute_topics', Response.PermError)
            return
        
        if topic_del is not None:
            topic_del.delete()
    
    try:
        db.session.commit()
        emit('create_minute_topics', Response.DeleteTopicSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit("create_minute_topics", Response.DeleteTopicError)

