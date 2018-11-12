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
    emit('get_notifications', notifications, room= user.id)


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
    user_regex = "(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)"
    mentioned = re.findall(user_regex, new_note.description)

    for u in mentioned:
        user = Users.query.filter_by(id= u).first()

        if user is not None:
            connection.execute(notifications_table, 
                user = u,
                type = NotificationType.MentionedInNote,
                destination = new_note.id
            )

            get_notifications(user)


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
    connection.execute(notifications_table,
        user = new_action.assigned_to,
        type = NotificationType.AssignedToAction,
        destination = new_action.id
    )

    user = Users(id = new_action.assigned_to)
    get_notifications(user)


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
        destination = new_committee.id
    )

    user = Users(id = new_committee.head)
    get_notifications(user)


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
            destination = new_request.id
        )
        
        user = Users(id = new_request.committee.head)
        get_notifications(user)
