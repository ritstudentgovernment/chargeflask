"""
filename: controllers.py
description: Controller for Users.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/07/17
"""

from flask_socketio import emit
from app.decorators import ensure_dict, get_user
from app import socketio, db
from app.users.models import Users, Roles
from app.users.users_response import Response
from app import saml_manager
from flask_login import login_user, current_user
from flask import redirect, jsonify
import ldap

@socketio.on('get_all_users')
def get_all_users():
    users = Users.query.filter_by().all()
    users_ser = [{"username": user.id, "name": user.first_name + " " + user.last_name} for user in users]
    emit('get_all_users', users_ser)
    return;

@socketio.on('add_user')
@get_user
def add_user(user, user_data):

    # Only admins can manually add other admins
    if user.is_admin == False:
        emit('add_user', Response.PermError)

    # Input validation for email
    if "@rit.edu" not in user_data["email"] and "@g.rit.edu" not in user_data["email"]:
        emit('add_user', Response.AddAdminEmailError)
        return;

    users = Users.query.filter_by().all()
    for user in users:
        if (user.id == user_data["id"]):
            emit('add_user', Response.UserAlreadyExistsError)
            return;

    # TODO add "user updated to admin success message"

    newUser = Users(id = user_data["id"])
    newUser.first_name = user_data.get("first_name", "")
    newUser.last_name = user_data.get("last_name", "")
    newUser.email = user_data.get("email", "")
    newUser.is_admin = user_data.get("is_admin", "")
    db.session.add(newUser)

    try:
        db.session.commit()
        emit('add_user', Response.AddSuccess)
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        emit('add_user', Response.DBError)


# setup acs response handler
@saml_manager.login_from_acs
def login_from_acs(acs):
    
    if acs.get('errors'):
        return jsonify({'errors': acs.get('errors')})
    elif not acs.get('logged_in'):
        return jsonify({"error": "login failed"})
    else:
        attributes = list(acs.get("attributes"))
        username = attributes[0][1][0]
        firstname = attributes[1][1][0]
        lastname = attributes[2][1][0]
        email = attributes[3][1][0]

        user = Users.query.filter_by(id = username).first()

        if user is None:
            user = Users(id = username)
            user.first_name = firstname
            user.last_name = lastname
            user.email = email

            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect('/')


@socketio.on('verify_auth')
@ensure_dict
@get_user
def verify(user, user_data):

    if not user:
        emit('verify_auth', Response.AuthError)
        return;

    emit('verify_auth', {
        'admin': user.is_admin,
        'username': user.id
    })


@socketio.on('auth')
@ensure_dict
def login_ldap(credentials):

    ldap_server = "ldaps://ldap.rit.edu"

    if credentials.get("username","") == "" or credentials.get("password","") == "":

        emit('auth', {'error': "Authentication error."})
        return;

    user_dn = "uid=" + credentials.get("username","") + ",ou=People,dc=rit,dc=edu"
    search_filter = "uid=" + credentials.get("username","")
    connect = ldap.initialize(ldap_server)

    try:

        connect.bind_s(user_dn, credentials.get("password",""))
        result = connect.search_s(user_dn,ldap.SCOPE_SUBTREE,search_filter)
        connect.unbind_s()

        values = result[0][1]
        username = values["uid"][0].decode('utf-8')
        firstname = values["givenName"][0].decode('utf-8')
        lastname = values["sn"][0].decode('utf-8')
        email = values["mail"][0].decode('utf-8')

        # Check if a user exists.
        if Users.query.filter_by(id = username).first() is not None:

            user = Users.query.filter_by(id = username).first()
            token = user.generate_auth()
            admin = user.is_admin
            emit('auth', {
                'token': token.decode('ascii'),
                'admin': admin,
                'username': username
            })

        else:

            user = Users(id = username)
            user.first_name = firstname
            user.last_name = lastname
            user.email = email

            db.session.add(user)
            db.session.commit()
            token = user.generate_auth()
            emit('auth', {'token': token.decode('ascii')})

    except ldap.LDAPError:
        connect.unbind_s()
        emit('auth', Response.AuthError)
        return;


##
## @brief      Changes a users role to ManagerUser,
##             AdminUser or NormalUser.
##
## @param      user       The user performing the edit.
## @param      user_data  JSON object containing:
##             
##             - username: username of the user with
##                         edited roles.
##             - role: AdminUser, ManagerUser or NormalUser.
##
## @emit       Success if role was set, PermError if user is not
##             an AdminUser, UserNotFound if user is not found,
##             RoleNotFound if role doesn't exist and DBError if
##             something went wrong in DB-side.
##
@socketio.on('edit_roles')
@ensure_dict
@get_user
def edit_roles(user, user_data):
    if not user.is_admin:
        emit('auth', Response.PermError)
        return;

    edit_user = Users.query.filter_by(id = user_data["username"]).first()

    if not edit_user:
        emit('edit_roles', Response.UserNotFound)
        return;

    try:
        role = Roles[user_data["role"]]
    except:
        emit('edit_roles', Response.RoleNotFound)
        return;

    if role == Roles.AdminUser:
        edit_user.is_admin = True
    elif role == Roles.ManagerUser:
        edit_user.is_admin = True
    else:
        edit_user.is_admin = False

    try:
        db.session.commit()
        emit('edit_roles', {"success": "Role set to " + role.value + "."})
    except Exception as e:
        db.session.rollback()
        emit('edit_roles', Response.DBError)
    return;
