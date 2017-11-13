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
## CanView:         View changes in Committees.
## CanContribute:   View actions, create notes and charges.
## CanCreate:       Can create Actions.
## CanEdit:         Can change heads, change status, remove
##                  members and transfer charges.
class Permissions():
    CanEdit = 4
    CanCreate = 3
    CanContribute = 2
    CanView = 1
