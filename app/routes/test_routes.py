"""
filename: test_routes.py
description: Tests for Routes.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 11/05/18
"""
import pytest
import config
from app import app

class TestRoutes(object):

    @classmethod
    def setup_class(self):
        self.app = app.test_client()
        app.config['DEBUG'] = False

    # Gets the view for login.
    def test_get_login(self):
        resp = self.app.get('/saml/login')
        assert resp.status == "302 FOUND"

    # Gets the view for logout.
    def test_get_logout(self):
        resp = self.app.get('/saml/logout')
        assert resp.status == "302 FOUND"

    # Gets the view for any route.
    def test_get_anything(self):
        resp = self.app.get('/anything')
        assert resp.status == "200 OK"
