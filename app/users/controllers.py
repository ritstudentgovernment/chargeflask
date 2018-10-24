"""
filename: controllers.py
description: Controller for Users.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/07/17
"""

from flask_socketio import emit
from app.check_data_type import ensure_dict, get_user
from app import socketio, db
from app.users.models import Users
from app.users.users_response import Response
from app import saml_manager
from flask_login import login_user, current_user
from flask import redirect
import ldap


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
        firstname = attributes[5][1][0]
        lastname = attributes[3][1][0]
        email = attributes[2][1][0]

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
