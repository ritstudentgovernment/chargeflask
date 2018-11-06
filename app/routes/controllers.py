"""
filename: controllers.py
description: Controller for Routes.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 11/05/18
"""
from flask import render_template, redirect
from app import app

# Route to shibboleth login.
@app.route('/saml/login')
def login_page():
	return redirect("/saml/login")

# Route to shibboleth logout.
@app.route('/saml/logout')
def logout_page():
	return redirect("/saml/logout")

# Route to everything else in the app.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")

# Route to get shibboleth metadata.
if app.config['DEBUG']:
	@app.route('/metadata/')
	def metadata():
	  saml = SamlRequest(request)
	  return saml.generate_metadata()
