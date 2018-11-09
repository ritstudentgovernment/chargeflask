from sqlalchemy.event import listens_for
from app.notes.models import Notes
from app.users.models import Users
from app.actions.models import Actions
from app.notifications.models import Notifications, NotificationType
from app import db
import re

USER_REGEX = "(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)"
notifications_table = Notifications.__table__.insert() 

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
    mentioned = re.findall(USER_REGEX, new_note.description)

    for u in mentioned:
        user = Users.query.filter_by(id= u).first()

        if user is not None:

            try:
                connection.execute(notifications_table, 
                    user = u,
                    type = NotificationType.MentionedInNote,
                    destination = new_note.id
                )
            except Exception as e:
                raise;


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
    try:
        connection.execute(notifications_table,
            user = new_action.assigned_to,
            type = NotificationType.AssignedToAction,
            destination = new_action.id
        )
    except Exception as e:
        raise;
