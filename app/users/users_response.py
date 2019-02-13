"""
filename: users_response.py
description: Responses for users module.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/12/18
"""

class Response():
    AuthError = {'error': 'Authentication error.'}
    PermError = {'error': 'Insufficient permissions to perform this action.'}
    DBError = {'error': 'Could not complete action.'}
    UserNotFound = {'error': 'User not found.'}
    RoleNotFound = {'error': 'Role not found.'}
