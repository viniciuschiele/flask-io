import json

from flask import Flask
from flask_io import FlaskIO, fields, post_load, Schema
from unittest import TestCase


class TestRequestBody(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.client = self.app.test_client()

    def test_invalid_payload_format(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            pass

        headers = {'content-type': 'application/json'}
        response = self.client.post('/resource', data='invalid data', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_invalid_field(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            self.assertEqual(type(user), User)
            self.assertEqual(user.username, 'user1')
            self.assertEqual(user.password, 'pass1')

        data = UserSchema().dump(User('user1', 'p'))

        headers = {'content-type': 'application/json'}
        response = self.client.post('/resource', data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_valid_fields(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            self.assertEqual(type(user), User)
            self.assertEqual(user.username, 'user1')
            self.assertEqual(user.password, 'pass1')

        data = UserSchema().dump(User('user1', 'pass1'))

        headers = {'content-type': 'application/json'}
        response = self.client.post('/resource', data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_missing_payload(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            pass

        response = self.client.post('/resource')
        self.assertEqual(response.status_code, 400)

    def test_no_content_type(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            self.assertEqual(type(user), User)
            self.assertEqual(user.username, 'user1')
            self.assertEqual(user.password, 'pass1')

        data = UserSchema().dump(User('user1', 'pass1'))

        response = self.client.post('/resource', data=json.dumps(data))
        self.assertEqual(response.status_code, 204)

    def test_invalid_content_type(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            pass

        data = UserSchema().dump(User('user1', 'pass1'))

        headers = {'content-type': 'application/data'}
        response = self.client.post('/resource', data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 415)

    def test_invalid_accept(self):
        @self.app.route('/resource', methods=['GET'])
        def test():
            return 'response'

        headers = {'accept': 'application/data'}
        response = self.client.get('/resource', headers=headers)
        self.assertEqual(response.status_code, 406)

    def test_accept_with_parameters(self):
        @self.app.route('/resource', methods=['GET'])
        def test():
            return 'response'

        headers = {'accept': 'application/json;indent=2'}
        response = self.client.get('/resource', headers=headers)
        self.assertEqual(response.status_code, 200)


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(Schema):
    username = fields.String()
    password = fields.String(validate=lambda n: len(n) >= 5)

    @post_load
    def make_object(self, data, many, partial):
        return User(**data)
