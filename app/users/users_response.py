"""
filename: users_response.py
description: Responses for users module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/18
"""

class Response():
    AddSuccess = {'success': 'User was added to the database'}
    AuthError = {'error': 'Authentication error.'}
    AddAdminEmailError = {'error': 'User email invalid. Must use RIT email.'}
    UserAlreadyExistsError = {'error': 'Username already exists'}
    UserAlreadyAdmin = {'error': 'This user is already an Admin'}
    PermError = {'error': 'Insufficient permissions to perform this action.'}
    DBError = {'error': 'Could not complete action.'}
    UserNotFound = {'error': 'User not found.'}
    RoleNotFound = {'error': 'Role not found.'}
