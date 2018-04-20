"""
filename: notes_response.py
description: Response messages for notes module.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/02/18
"""

class Response():
	AddSuccess = {"success": "Note has been added to action."}
	AddError = {"error": "Note couldn't be added to action."}
	ModifySuccess = {"success": "Note has modified"}
	ModifyError = {"error": "Note has not modified"}
	UsrNotAuth = {"error": "User not authorized."}
	ActionDoesntExist = {'error': "Action doesn't exist."}
	NoteDoesntExist = {'error': "Note doesn't exist."}
