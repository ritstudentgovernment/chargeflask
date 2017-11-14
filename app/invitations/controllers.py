"""
filename: controllers.py
description: Controllers for email invitations.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/17
"""

from flask_socketio import emit
from app import app, db, mail, socketio
from app.users.models import Users
from app.invitations.models import Invitations
from app.invitations.invitations_response import Response
from flask import render_template
from flask_mail import Message
from sqlalchemy import and_
import time


##
## @brief      Sends an invitation to join a committee
##             when user doesn't exist in ChargeTracker.
##
## @param      committee       The committee to join.
## @param      new_user        The user to be invited.
##
## @return     True if email sent, False if not.
##
def send_invite(new_user, committee):

    invite = and_(
        Invitations.user_name == new_user,
        Invitations.committee_id == committee.id,
        Invitations.isInvite == True
    )

    if Invitations.query.filter(invite).first() is not None:
        return Response.InviteExists

    invitation = Invitations(
        user_name= new_user,
        committee= committee,
        committee_id = committee.id,
        isInvite= True
    )

    try:

        db.session.add(invitation)
        db.session.commit()

        msg = Message("You're Invited")
        msg.sender=("SG TigerTracker", "sgnoreply@rit.edu")
        msg.recipients = [new_user + "@rit.edu"]
        msg.subtype = "related"
        msg.html = render_template(
            'committee_invitation.html',
            user_name= new_user,
            committee_name= committee.title,
            committee_head= committee.head,
            time_stamp= time.time(),
            invite_url= invitation.id
        )

        # Attach sglogo to email.
        with app.open_resource("static/sg-logo.png") as fp:
            msg.attach("static/sg-logo.png", "image/png", fp.read(), headers={'Content-ID': '<sg-logo>'})

        # Attach paw to email.
        with app.open_resource("static/paw.png") as fp:
            msg.attach("static/paw.png", "image/png", fp.read(), headers={'Content-ID': '<sg-paw>'})

        mail.send(msg)
        return Response.InviteSent
    except Exception as e:

        db.session.rollback()
        return Response.InviteError


##
## @brief      Sends a request email to join a committee 
##             to the committee head.
##
## @param      new_user   The user to be added.
## @param      committee  The committee to join.
##
## @return     True if email sent, False if not.
##
def send_request(new_user, committee):

    invite = and_(
        Invitations.user_name == new_user.id,
        Invitations.committee_id == committee.id,
        Invitations.isInvite == False
    )

    if Invitations.query.filter(invite).first() is not None:
        return Response.RequestExists

    invitation = Invitations(
        user_name= new_user.id,
        committee= committee,
        committee_id = committee.id,
        isInvite= False
    )
    
    try:

        db.session.add(invitation)
        db.session.commit() 

        msg = Message("Great news, " + new_user.id + " wants to join!")
        msg.sender = ("SG TigerTracker", "sgnoreply@rit.edu")
        msg.recipients = [committee.head + "@rit.edu"]
        msg.subtype = "related"
        msg.html = render_template(
            'committee_request.html', 
            user_name= new_user.id,
            committee_head= committee.head,
            committee_name= committee.title,
            time_stamp= time.time(),
            resquest_url= invitation.id
        )

        # Attach sglogo to email.
        with app.open_resource("static/sg-logo.png") as fp:
            msg.attach("static/sg-logo.png", "image/png", fp.read(), headers={'Content-ID': '<sg-logo>'})

        # Attach paw to email.
        with app.open_resource("static/paw.png") as fp:
            msg.attach("static/paw.png", "image/png", fp.read(), headers={'Content-ID': '<sg-paw>'})

        mail.send(msg)
        return Response.RequestSent
    except Exception as e:
        
        db.session.rollback()
        return Response.RequestError


##
## @brief      Gets the data for a specific invitation/request.
##
## @param      user_data  The data to display a specific invitation.
## 
##                        Contains the keys (all required):
##                        - token: The token of the authenticated user
##                        - invitation_id: Id of invitation/request.
##
## @emit       Data of a specific invitation or errors.
##
@socketio.on('get_invitation')
def get_invitation(user_data):

    invitation = Invitations.query.filter_by(id = user_data["invitation_id"]).first()
    user = Users.verify_auth(user_data["token"])

    if invitation is None:
        emit("get_invitation", Response.InviteDoesntExist)
        return

    if user is None:
        emit("get_invitation", Response.NotAuthenticated)
        return

    committee = invitation.committee

    # Check if user should be able to view
    # invitation.
    if (committee.head == user.id or
        user.is_admin or
        user.id == invitation.user_name):

        invitation_data = {
            "committee_id": committee.id,
            "committee_head": committee.head,
            "committee_title": committee.title,
            "current_user": user.id,
            "invite_user": invitation.user_name,
            "is_invite": invitation.isInvite
        }

        emit("get_invitation", invitation_data)
    else:

        emit("get_invitation", Response.IncorrectPerms)


##
## @brief      Changes the status of an invitation/request.
##
## @param      user_data  The data to modify a specific invitation.
## 
##                        Contains the keys (all required):
##                        - token: The token of the authenticated user
##                        - invitation_id:  Id of invitation/request.
##                        - status: True to accept, false otherwise.
##
## @emit       UserAdded, InviteDeleted or errors.
##
@socketio.on('set_invitation')
def set_invitation(user_data):
    
    invitation = Invitations.query.filter_by(id = user_data["invitation_id"]).first()
    user = Users.verify_auth(user_data["token"])

    if invitation is None:
        emit("set_invitation", Response.InviteDoesntExist)
        return

    if user is None:
        emit("set_invitation", Response.NotAuthenticated)
        return

    if "status" not in user_data:
        emit("set_invitation", Response.InvalidStatus)
        return

    if type(user_data["status"]) != type(True):
        emit("set_invitation", Response.InvalidStatus)
        return

    com_head = Users.query.filter_by(id= invitation.committee.head).first()
    com_id = invitation.committee.id
    token = user_data["token"]

    # If invitation, use the committe heads token.
    if invitation.isInvite:

        token = com_head.generate_auth()
    else:

        if com_head != user or not user.is_admin:
            emit("set_invitation", Response.IncorrectPerms)
            return

    if user_data["status"] == True:

        add_data = {
            "token": token,
            "committee_id": com_id,
            "user_id": invitation.user_name
        }

        from app.members.controllers import add_to_committee
        add_to_committee(add_data)

        emit("set_invitation", Response.InviteAccept)
    else:
        emit("set_invitation", Response.InviteDeny)

    # Remove the invitation.
    db.session.delete(invitation)
