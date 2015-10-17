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
from flask_io import fields, FlaskIO, Error, Schema
from unittest import TestCase


class TestResponseStatus(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.client = self.app.test_client()

    def test_unauthorized(self):
        @self.app.route('/resource', methods=['POST'])
        def test():
            return self.io.unauthorized(Error('required', 'Login required', 'header', 'Authorization'))

        response = self.client.post('/resource')
        self.assertEqual(response.status_code, 401)

    def test_none_with_envelope(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.marshal_with(UserSchema, envelope='users')
        def test():
            return None

        response = self.client.post('/resource')

        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(data.get('users', 'missing'), None)

    def test_empty_list_with_envelope(self):
        @self.app.route('/resource', methods=['POST'])
        @self.io.marshal_with(UserSchema, envelope='users')
        def test():
            return []

        response = self.client.post('/resource')

        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(data.get('users'), [])

    def test_no_content(self):
        @self.app.route('/resource', methods=['POST'])
        def test():
            return None

        response = self.client.post('/resource')

        self.assertEqual(response.status_code, 204)
        self.assertTrue(response.content_type.startswith('text/html'))

    def test_error(self):
        @self.app.route('/resource', methods=['POST'])
        def test():
            raise Exception('expected error in test_error')

        response = self.client.post('/resource')

        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.content_type.startswith('application/json'))

        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(type(data.get('errors')), list)
        self.assertEqual(len(data.get('errors')), 1)



class UserSchema(Schema):
    username = fields.String()
