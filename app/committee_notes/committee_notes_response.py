"""
filename: charges_response.py
description: Responses for charges module.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/23/18
"""

class Response():
    AddSuccess = {'success': 'Committee note successfully created.'}
    AddError = {'error': 'Committee note couldnt be created, check data.'}
    CommitteeDoesntExist = {'error': "Committee doesn't exist."}
    UsrNotAuth = {'error': "User is not authorized to do that."}
