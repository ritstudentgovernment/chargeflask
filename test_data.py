from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import *
from sqlalchemy_utils import ChoiceType
from flask_socketio import SocketIO
from mimesis import Text, Address, Person
import random
person = Person()
text = Text()
address = Address()

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')

# Import each module created.
from app.users.controllers import *
from app.committees.controllers import *
from app.members.controllers import *
from app.charges.controllers import *
from app.actions.controllers import *
from app.actions.models import *
from app.committees.models import *
from app.notes.models import *
from app.committee_notes.models import *


db.drop_all()
db.create_all()


def main():
    # Create the app and add configuration.
    db = SQLAlchemy(app)
    db.drop_all()
    db.create_all()
    make_users()
    make_committees()
    make_charges()
    make_actions()
    make_notes()
    make_committee_notes()


def make_users():
    for count in range(0, 100):
        username = 'TestUser'+str(count)
        user = Users(id = username)
        user.first_name = person.name()
        user.last_name = person.last_name()
        user.email = username + "@test.com"
        user.is_admin = False
        db.session.add(user)
        db.session.commit()

    for count in range(0, 10):
        username = 'AdminUser'+str(count)
        user = Users(id = username)
        user.first_name = person.name()
        user.last_name = person.last_name()
        user.email = username + "@test.com"
        user.is_admin = True
        db.session.add(user)
        db.session.commit()



def make_committees():

    for count in range(0, 10):
        committeeID = 'TestCommittee'+str(count)
        committee = Committees(id=committeeID)
        committee.location = address.city()
        committee.title = text.title()
        committee.description = text.sentence()
        committee.meeting_day = 2
        committee.meeting_time = 1300
        addID = count*10
        committee.head = 'TestUser'+str(addID)
        for countID in range(1,10):
            newID = (int)(addID + countID)
            committee.members.append(Users.query.filter_by(id = 'TestUser'+str(newID)).first())

        com_img = base64.b64decode("R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==")
        committee.committee_img = com_img

        db.session.add(committee)
        db.session.commit()

def make_charges():
    charge_count = 0
    for committee_id in range(0,10):
        committee_id_str = 'TestCommittee'+str(committee_id)

        for chargeID in range(0,2):
            charge = Charges(id=charge_count)
            charge.title = text.title()
            charge.author = 'TestUser'+str(committee_id*10)
            charge.description = text.sentence()
            charge.committee = committee_id_str
            charge.objectives = [text.word(), text.word()]
            charge.schedule = [text.word(), text.word()]
            charge.resources = [text.word(), text.word()]
            charge.stakeholders = [text.word(), text.word()]
            charge.priority = random.randint(0,2)
            charge.status = random.randint(0,7)
            charge_count = charge_count+1
            db.session.add(charge)
            db.session.commit()

def make_actions():
    for committee_id in range(0,10):
        committee_id_str = 'TestCommittee'+str(committee_id)


        for action_id in range (1,10):
            new_action_id = committee_id*10 + action_id
            action = Actions(id = new_action_id)
            action.title = text.title()
            action.author = 'TestUser'+str(committee_id*10)
            action.description = text.sentence()
            action.assigned_to = 'TestUser'+str(new_action_id)
            action.charge = committee_id*2 + (action_id%2)
            action.status = random.randint(0,6)

            db.session.add(action)
            db.session.commit()


def make_notes():
    for committee_id in range(0,10):
        committee_id_str = 'TestCommittee'+str(committee_id)


        for note_id in range (1,10):
            new_note_id = committee_id*10 + note_id
            note = Notes(id = new_note_id)
            note.description = text.sentence()+' '+text.sentence()+' '+text.sentence()
            note.author = 'TestUser'+str(new_note_id)
            note.charge = committee_id*2 + (note_id%2)

            db.session.add(note)
            db.session.commit()

def make_committee_notes():
    for committee_id in range(0,10):
        committee_id_str = 'TestCommittee'+str(committee_id)

        new_committee_note_id = committee_id
        committee_note = CommitteeNotes(id = new_committee_note_id)
        committee_note.description =  text.sentence()+' '+text.sentence()+' '+text.sentence()
        committee_note.author = "TestUser"+ str(committee_id*10)
        committee_note.committee = 'TestCommittee'+str(committee_id)

        db.session.add(committee_note)
        db.session.commit()

if __name__== "__main__":
  main()
