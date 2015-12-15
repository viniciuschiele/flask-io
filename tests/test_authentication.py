from flask import Flask, request
from flask_io import FlaskIO, errors
from flask_io.authentication import Authenticator
from unittest import TestCase


class TestAuthorization(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.client = self.app.test_client()

    def test_with_token(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.authenticators(TokenAuthenticator)
        def test():
            pass

        response = self.client.get('/resource', headers={'Authorization': 'token'})
        self.assertEqual(response.status_code, 204)

    def test_missing_token(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.authenticators(TokenAuthenticator)
        def test():
            pass
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 401)


class TokenAuthenticator(Authenticator):
    def authenticate(self):
        if request.headers.get('Authorization') is None:
            raise errors.AuthenticationFailed()
        return 'user', 'auth'
