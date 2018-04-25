"""
filename: charges_response.py
description: Responses for charges module.
created by: Chris Lemelin (cxl8826@rit.edu)
created on: 04/23/18
"""

class Response():
    AddSuccess = {'success': 'Committee note successfully created.'}
    AddError = {'error': 'Committee note couldnt be created, check data.'}
    ModifySuccess = {"success": "Committee note has modified"}
    ModifyError = {"error": "Committee note has not modified"}
    CommitteeDoesntExist = {'error': "Committee doesn't exist."}
    CommitteeNoteDoesntExist = {'error': "Committee note doesn't exist."}
    UsrNotAuth = {'error': "User is not authorized to do that."}
    UsrDoesntExist = {'error': "User doesn't exist."}
