"""
filename: minutes_response.py
description: Response messages for members module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/11/17
"""

class Response():

    # General Responses
    InvalidData = {"error": "Input data is not correct."}
    PermError = {"error": "User doesn't have permissions to complete this action."}
    UserDoesntExist = {"error": "User doesn't exist."}
    CommitteeDoesntExist = {"error": "Committee doesn't exist."}
    
    # Minute Responses
    AddMinuteSuccess = {"success": "Minute has been added to committee."}
    AddMinuteError = {"error": "Minute couldn't be added to committee."}
    MinuteDoesntExist = {"error": "Minute doesn't exist."}
    EditSuccess = {"success": "Minute successfully edited."}
    EditError = {"error": "Minute couldn't be edited."}
    DeleteMinuteSuccess =  {"error": "Minute successfully deleted."}
    DeleteMinuteError =  {"error": "Minute couldn't be deleted."}
