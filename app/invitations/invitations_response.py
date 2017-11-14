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
	InviteDoesntExist = {"error": "Invitation doesn't exist."}
	InviteAccept = {"success": "Invitation has been accepted."}
	InviteDeny = {"error": "Invitation has been denied."}
	RequestExists = {"error": "User has already requested to join committee."}
	UserIsPart = {"error": "User is already part of this committee."}
	NotAuthenticated = {"error": "User is not authenticated"}
	InvalidStatus = {"error": "Please insert a valid status."}
	IncorrectPerms = {"error": "Incorrect user permissions."}