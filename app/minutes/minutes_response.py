"""
filename: minutes_response.py
description: Response messages for members module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/11/17
"""

class Response():
    UserDoesntExist = {"error": "User or committee don't exist."}
    InvalidData = {"error": "Input data is not correct."}
    PermError = {"error": "User doesn't have permissions to create minute."}
    AddSuccess = {"success": "Minute has been added to committee."}
    AddError = {"error": "Minute couldn't be added to committee."}
