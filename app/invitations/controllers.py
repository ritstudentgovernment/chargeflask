"""
filename: controllers.py
description: Controllers for email invitations.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/17
"""

from app import app, db, mail
from app.invitations.models import Invitations
from app.invitations.invitations_response import Response
from flask import render_template
from flask_mail import Message
from sqlalchemy import and_


##
## @brief      Sends an invitation to join a committee
##             when user doesn't exist in ChargeTracker.
##
## @param      committee       The committee to join.
## @param      send_to         The user to be invited.
##
## @return     True if email sent, False if not.
##
def send_invite(new_user, committee):

    invite = and_(
        Invitations.user_name == new_user,
        Invitations.committee == committee.id
    )

    if Invitations.query.filter(invite).first() is not None:
        return Response.InviteExists

    invitation = Invitations(
        user_name= new_user,
        committee= committee.id,
        isInvite= True
    )

    try:

        db.session.add(invitation)
        db.session.commit()

        msg = Message("You're Invited")
        msg.sender=("SG TigerTracker", "sgnoreply@rit.edu")
        msg.recipients = [send_to + "@rit.edu"]
        msg.html = render_template(
            'committee_invitation.html',
            user_name= send_to,
            committee_name= committee.title,
            committee_head= committee.head,
            invite_url= invitation.id
        )

        mail.send(msg)
        return Response.InviteSent
    except Exception as e:

        print(e)
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
        Invitations.committee == committee.id
    )

    if Invitations.query.filter(invite).first() is not None:
        return Response.RequestExists

    invitation = Invitations(
        user_name= new_user.id,
        committee= committee.id,
        isInvite= False
    )
    
    try:

        db.session.add(invitation)
        db.session.commit()

        msg = Message("Great news, " + new_user.id + " wants to join!")
        msg.sender = ("SG TigerTracker", "sgnoreply@rit.edu")
        msg.recipients = [committee.head + "@rit.edu"]        
        msg.html = render_template(
            'committee_request.html', 
            user_name= new_user.id,
            committee_head= committee.head,
            committee_name= committee.title,
            resquest_url= invitation.id
        )

        mail.send(msg)
        return Response.RequestSent
    except Exception as e:

        print(e)
        db.session.rollback()
        return Response.RequestError
