"""
filename: actions_response.py
description: Responses for actions module.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 03/23/18
"""

class Response():
	AddSuccess = {'success': 'Action successfully created.'}
	AddError = {'error': 'Action couldnt be created, check data.'}
	UsrChargeDontExist = {'error': 'User or Charge do not exist.'}
	UsrNotAuth = {'error': "User is not authorized to create an Action"}
	ActionDoesntExist = {'error': "Action doesn't exist"}
	
