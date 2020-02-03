"""
filename: controllers.py
description: Controllers for Notifications.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 11/08/18
"""

from sqlalchemy.event import listens_for
from app.notes.models import Notes
from app.users.models import Users
from app.actions.models import Actions
from app.committees.models import Committees
from app.invitations.models import Invitations
from app.notifications.models import Notifications, NotificationType
from app.decorators import ensure_dict, get_user
from app import db, socketio
from flask_socketio import emit
import re

notifications_table = Notifications.__table__.insert() 

##
## @brief      Gets the notifications for a user.
##
## @param      user       The user object.
## @param      user_data  The user data.
##
## @return     An array of notifications for the user.
##
@socketio.on('get_notifications')
@ensure_dict
@get_user
def get_notifications(user, user_data):
    notifications = Notifications.query.filter_by(user = user.id).all()
    noti_ser = [{"id": c.id, "user": c.user, "type": c.type.value, "destination": c.destination, "viewed": c.viewed, "message": c.message, "redirect": c.redirect} for c in notifications]
    emit('get_notifications', noti_ser)


##
## @brief      Sends new notifications to a user.
##
## @param      user  The user to send notifications to.
##
## @return     An array of notifications for the user.
##
def send_notifications(user):
    notifications = Notifications.query.filter_by(user = user).all()
    noti_ser = [{"id": c.id, "user": c.user, "type": c.type.value, "destination": c.destination, "viewed": c.viewed, "message": c.message, "redirect": c.redirect} for c in notifications]
    emit('get_notifications', noti_ser, room= user)


##
## @brief      Looks for mentions in tasks notes,
##             notifies the user that was mentioned. 
##
## @param      mapper      The database mapper.
## @param      connection  The connection to the database.
## @param      new_note    The new note being added.
##
## @return     void
##
@listens_for(Notes, 'after_insert')
def new_note(mapper, connection, new_note):
    # Finds usernames when they are indicated with the @ symbol, stores them in 'mentioned'
    user_regex = "(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)"
    mentioned = re.findall(user_regex, new_note.description)
    action = Actions.query.filter_by(id= int(new_note.action)).first()

    for u in mentioned:
        user = Users.query.filter_by(id= u).first()
        if user is not None:
            connection.execute(notifications_table, 
                user = u,
                type = NotificationType.MentionedInNote,
                destination = new_note.id,
                viewed = False,
                message = create_message(NotificationType.MentionedInNote, action.title),
                redirect = create_redirect_string(NotificationType.MentionedInNote, action.charge)
            )
            send_notifications(u)


##
## @brief      Notifies a user when an action has been
##             created for them. 
##
## @param      mapper      The database mapper.
## @param      connection  The connection to the database.
## @param      new_action  The new action being added.
##
## @return     void
##
@listens_for(Actions, 'after_insert')
def new_action(mapper, connection, new_action):
    print(new_action.charge)
    connection.execute(notifications_table,
        user = new_action.assigned_to,
        type = NotificationType.AssignedToAction,
        destination = new_action.id,
        viewed = False,
        message = create_message(NotificationType.AssignedToAction, new_action.title),
        redirect = create_redirect_string(NotificationType.AssignedToAction, new_action.charge)
    )
    send_notifications(new_action.assigned_to)


##
## @brief      Notifies a user when made the head
##             of a committee.
##
## @param      mapper         The database mapper
## @param      connection     The connection to the database
## @param      new_committee  The new committee being added.
##
## @return     void
##
@listens_for(Committees, 'after_insert')
def new_committee(mapper, connection, new_committee):

    connection.execute(notifications_table,
        user = new_committee.head,
        type = NotificationType.MadeCommitteeHead,
        destination = new_committee.id,
        viewed = False,
        message = create_message(NotificationType.MadeCommitteeHead, new_committee.title),
        redirect = create_redirect_string(NotificationType.MadeCommitteeHead, new_committee.id)
    )
    send_notifications(new_committee.head)


##
## @brief      Notifies a committee head when
##             someone wants to join their committee.
##
## @param      mapper       The database mapper
## @param      connection   The connection to the database
## @param      new_request  The new request to join
##
## @return     void
##
@listens_for(Invitations, 'after_insert')
def new_request(mapper, connection, new_request):
    if not new_request.isInvite:
        connection.execute(notifications_table,
            user = new_request.committee.head,
            type = NotificationType.UserRequest,
            destination = new_request.id,
            viewed = False,
            message = create_message(NotificationType.UserRequest, new_request.id),
            redirect = create_redirect_string(NotificationType.UserRequest, new_request.id)
        )
        send_notifications(new_request.committee.head)

##
## @brief      Updates the notification when it has been viewed.
##
## @param      user       The user object.
## @param      user_data  The user's token.
##
## @return     An array of notifications for the user.
##
@socketio.on('update_notification')
@ensure_dict
@get_user
def update_notification(user, user_data):
    notification = Notifications.query.filter_by(id = user_data["notificationId"]).first()
    notification.viewed = True 
    try:
        db.session.commit()
        emit('update_notification', {"success": "Notification set to viewed."})
    except Exception as e:
        db.session.rollback()
        emit('update_notification', {"error": "Notification not updated correctly."})
    return;

##
## @brief      Deletes the notification from the DB
##
## @param      user       The user object.
## @param      user_data  The user's token.
##
## @return     An array of notifications for the user.
##
@socketio.on('delete_notification')
@ensure_dict
@get_user
def delete_notification(user, user_data):
    notification = Notifications.query.filter_by(id = user_data["notificationId"]).first()
     
    try:
        db.session.delete(notification)
        emit('delete_minute', {"success": "Notification deleted."})
    except:
        db.session.rollback()
        db.session.flush()
        emit('delete_minute', {"error": "Notification was not deleted."})

##
## @brief      Creates the message for the notification on the frontend
##
## @return     the notification message to be displayed on the frontend.
##
def create_message(notificationType, message):
    
    if (notificationType is NotificationType.MadeCommitteeHead):
        message = 'You have been made the head of the committee: ' + message
    elif (notificationType is NotificationType.AssignedToAction): 
        message = 'You have been assigned to the task: ' + message
    elif (notificationType is NotificationType.MentionedInNote):
        message = 'You have been mentioned in a note. In the task: ' + message
    elif (notificationType is NotificationType.UserRequest):
        message = 'A user requests for you to close the charge: ' + message #TODO this needs updating

    return str(message)

##
## @brief      Creates the redirect string for the notification on the frontend
##
## @return     the redirect string to be used on the frontend when the user opens the notification
##
def create_redirect_string(notificationType, destination):

    destination = str(destination)

    if (notificationType is NotificationType.MadeCommitteeHead):
        redirect = '/committee/' + destination
    elif (notificationType is NotificationType.AssignedToAction):
        redirect = '/charge/' + destination
    elif (notificationType is NotificationType.MentionedInNote):
        redirect = '/charge/' + destination
    elif (notificationType is NotificationType.UserRequest):
        redirect = '/committee/' + destination

    return str(redirect)
