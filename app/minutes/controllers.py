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
        'date': minute.date,
        'committee_id': minute.committee_id,
        'topics': [{"topic": t.topic, "body": t.body} for t in minute.topics]
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
            'private': minute.private,
            'date': minute.date,
            'committee_id': minute.committee_id,
            'topics': [{"topic": t.topic, "body": t.body} for t in minute.topics]
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
##             - date (Integer)           Epoch date of minute creation.
##             - private (Boolean)        True if minute is private.
##             - topics ([Object])        (optional) If defined, check add_topics.
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
        # Delete all the topics for this minute.
        for topic in minute.topics:
            db.session.delete(topic)
        
        db.session.delete(minute)
        emit('delete_minute', Response.DeleteMinuteSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit('delete_minute', Response.DeleteMinuteError)


## @brief      Adds a list of minute topics
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - minute_id (Integer)   the id of the minute.
##             - topics ([Object])     Contains an array of objects,
##                                      if defined it contains the keys:
##
##                                     - topic (String): Topic title.
##                                     - body (String): Topic body.
##
## @emit       Emits AddTopicSuccess on list creation.
##
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


## @brief      Deletes topic(s)
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - topics ([Object]) The topic objects to delete.
##
## @emit       Emits DeleteTopicSuccess on deletion.
##
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
        
        if user.id != topic_del.minute.committee.head and not user.is_admin:
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


## @brief      Updates topic(s)
##
## @param      user         The user object
## @param      user_data    Contains the following keys:
##             
##             - topics ([Object]) The topic objects to update.
##
## @emit       Emits UpdateTopicSuccess on update.
##
@socketio.on('update_minute_topics')
@ensure_dict
@get_user
def update_topics(user, user_data):

    if user is None:
        emit('update_minute_topics', Response.UserDoesntExist)
        return
    
    if "topics" not in user_data:
        emit('update_minute_topics', Response.InvalidData)
        return
    
    try:
        for topic in user_data["topics"]:
            topic_upd = Topics.query.filter_by(id = topic.get("id", -1)).first()

            if topic_upd is None:
                emit('update_minute_topics', Response.InvalidData)
                return

            membership = topic_upd.minute.committee.members.filter_by(member= user).first()
    
            if (user.id != topic_upd.minute.committee.head and
                not user.is_admin and
                (membership is None or membership.role != Roles.MinuteTaker)):
                emit('update_minute_topics', Response.PermError)
                return
            
            topic_upd.title = topic["topic"]
            topic_upd.body = topic["body"]
            db.session.commit()
        emit('update_minute_topics', Response.UpdateTopicSuccess)
    except:
        db.session.rollback()
        db.session.flush()
        emit('update_minute_topics', Response.UpdateTopicError)
        return
