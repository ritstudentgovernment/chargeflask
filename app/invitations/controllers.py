"""
filename: controllers.py
description: Controllers for email invitations.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/17
"""

from app import app, mail
from flask import render_template
from flask_mail import Message


##
## @brief      Sends an invitation to join a committee
##             when user doesn't exist in ChargeTracker.
##
## @param      invited_by      User that send invitation.
## @param      committee_name  The committee name to join.
## @param      send_to         The user to be invited.
##
## @return     True if email sent, False if not.
##
def send_invite(invited_by, committee_name, send_to):
    msg = Message("You're Invited")
    msg.sender=("SG TigerTracker", "sgnoreply@rit.edu")
    msg.recipients = [send_to + "@rit.edu"]
    msg.html = render_template('committee_invitation.html',
                                user_name= send_to,
                                committee_name= committee_name,
                                committee_head= invited_by)

    try:

        mail.send(msg)
        return True
    except Exception as e:

        print(e)
        return False


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
    msg = Message("Great news, " + new_user + " wants to join!")
    msg.sender = ("SG TigerTracker", "sgnoreply@rit.edu")
    msg.recipients = [committee.head + "@rit.edu"]
    msg.html = render_template('committee_request.html', 
                                user_name= new_user,
                                committee_head= committee.head,
                                committee_name= committee.title)

    try:

        mail.send(msg)
        return True
    except Exception as e:

        print(e)
        return False
