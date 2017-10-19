"""
filename: controllers.py
description: Controllers for email invitations.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/17
"""

class Response():
	RequestSent = {"success": "Request to join has been sent."}
	InviteSent = {"success": "Invitation has been sent."}
	InviteError = {"error": "Invitation couldn't be sent."}
	RequestError = {"error": "Request couldn't be sent."}
	InviteExists = {"error": "User has already been invited to this committee."}
	RequestExists = {"error": "User has already requested to join committee."}
	UserIsPart = {"error": "User is already part of this committee."}
