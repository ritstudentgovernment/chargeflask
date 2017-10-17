"""
filename: controllers.py
description: Controllers for email invitations.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/17
"""

from app import app, mail
from flask_mail import Message


def send_invite(invited_by, send_to):
    msg = Message("You're Invited", sender=("SG TigerTracker","sgnoreply@rit.edu"), recipients = ["oed7416@rit.edu"])
    msg.body = "You were invited!"

    try:
        mail.send(msg)
    except Exception as e:
        print(e)
