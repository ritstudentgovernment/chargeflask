"""
filename: members_response.py
description: Response messages for members module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/11/17
"""

class Response():
	ComDoesntExist = {"error": "Committee doesn't exist."}
	AddSuccess = {"success": "User has been added to committee"}
	AddError = {"error": "User couldn't be added to committee"}
	RequestSent = {"success": "Request to join has been sent"}
	UserDoesntExist = {"error": "User or committee don't exist."}
	RemoveSuccess = {"success": "Member has been removed from committee"}
	RemoveError = {"error": "Member couldn't be removed from committee."}
	PermError = {"error": "User doesn't have permissions to remove members."}