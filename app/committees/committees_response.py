"""
filename: committees_response.py
description: Responses for committees module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/17
"""

class Response():
	ComDoesntExist = {'error': "Committee doesn't exist."}
	AddSuccess = {'success': 'Committee succesfully created'}
	AddError = {"error": "Committee couldn't be created, check data."}
	AddExists = {'error': "Committee already exists."}
	EditSuccess = {"success": "Committee succesfully edited."}
	EditError = {"error": "Committee couldn't be edited, check data."}
	UsrDoesntExist = {'error': "User doesn't exist or is not admin."}

