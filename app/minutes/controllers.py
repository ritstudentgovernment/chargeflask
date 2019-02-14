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

@socketio.on('get_minute')
@ensure_dict
@get_user
def get_minute(user, user_data):
    minute = Minutes.query.filter_by(id= user_data.get("minute_id", "")).first()
    
    if minute is None or user is None:
        emit('get_minute', Response.MinuteDoesntExist)
        return
    
    committee = minute.committee 

    membership = committee.members.filter_by(member = user).first()

    if minute.private and (membership is None or not user.is_admin or committee.head != user.id):
        emit('get_minute', Response.PermError)
        return
    
    emit('get_minute', minute)

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
            'date': minute.date,
            'committee_id': minute.committee_id,
            'topics': [{"topic": t.topic, "body": t.body} for t in minute.topics]
        })
    emit('get_minutes', minute_data)


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
    minute.private = user_data["private"]

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
def delete_topics(user, user_data):

    if user is None:
        emit('delete_minute_topics', Response.UserDoesntExist)
        return
    
    if "topics" not in user_data:
        emit('delete_minute_topics', Response.InvalidData)
        return
    
    for topic in user_data["topics"]:
        topic_del = Topics.query.filter_by(id = topic.get("id", -1)).first()

        if topic_del is None:
            emit('delete_minute_topics', Response.InvalidData)
            return
        
        if user.id != topic_del.minute.committee.head and user.is_admin == False:
            emit('delete_minute_topics', Response.PermError)
            return
        
        db.session.delete(topic_del)
    
    try:
        db.session.commit()
        emit('delete_minute_topics', Response.DeleteTopicSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit("delete_minute_topics", Response.DeleteTopicError)

