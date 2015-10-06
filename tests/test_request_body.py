# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from flask import Flask
from flask_io import FlaskIO
from marshmallow import fields, post_load, Schema
from unittest import TestCase


class TestRequestBody(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.client = self.app.test_client()

    def test_invalid_body(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            self.assertEqual(type(user), User)
            self.assertEqual(user.username, 'user1')
            self.assertEqual(user.password, 'pass1')

        data = UserSchema().dump(User('user1', 'p')).data

        headers = {'content-type': 'application/json'}
        response = self.client.post('/resource', data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_valid_body(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            self.assertEqual(type(user), User)
            self.assertEqual(user.username, 'user1')
            self.assertEqual(user.password, 'pass1')

        data = UserSchema().dump(User('user1', 'pass1')).data

        headers = {'content-type': 'application/json'}
        response = self.client.post('/resource', data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_no_content_type(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.from_body('user', UserSchema)
        def test(user):
            self.assertEqual(type(user), User)
            self.assertEqual(user.username, 'user1')
            self.assertEqual(user.password, 'pass1')

        data = UserSchema().dump(User('user1', 'pass1')).data

        response = self.client.post('/resource', data=json.dumps(data))
        self.assertEqual(response.status_code, 204)


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(Schema):
    username = fields.String()
    password = fields.String(validate=lambda n: len(n) >= 5)

    @post_load
    def make_object(self, data):
        return User(**data)
