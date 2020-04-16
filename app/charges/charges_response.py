"""
filename: charges_response.py
description: Responses for charges module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 12/05/17
"""

class Response():
	AddSuccess = {'success': 'Charge successfully created.'}
	AddError = {'error': 'Charge couldnt be created, check data.'}
	UsrChargeDontExist = {'error': 'User or charge does not exist.'}
	InvalidTitle = {'error': 'Charge title is invalid.'}
	InvalidPriority = {'error': 'Invalid priority level.'}
	EditError = {'error': 'Couldn\'t edit charge.'}
	EditSuccess = {'success': 'Charge successfully edited.'}
	CloseSuccess = {'success': 'Charge successfully closed.'}
	CloseError = {'error': 'Charge could not be closed.'}
	CloseRequestSuccess = {'success': 'Your request has been sent to the Admin.'}
	PermError = {'error': 'Insufficient permissions to perform this action.'}