"""
filename: permissions.py
description: User permissions for
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 10/26/17
"""


##
## @brief           Permission categories for users.
##                  A bigger permission number contains the
##                  privileges of a lesser number.
## 
## - CanView:         View changes in Committees.
## - CanContribute:   View actions, create notes and charges.
## - CanCreate:       Can create Actions.
## - CanEdit:         Can change heads, change status, remove
##                  members and transfer charges.
class Permissions():
	
	## Change heads, status, remove members and transfer charges.
    CanEdit = 4

    ## Can create Actions.
    CanCreate = 3

    ## View actions, create notes and charges.
    CanContribute = 2
    
    ##  View changes in Committees.
    CanView = 1
