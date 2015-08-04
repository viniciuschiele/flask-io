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

from flask import Flask
from flask_io import FlaskIO
from flask_io import fields
from unittest import TestCase


class TestRequestArgs(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.client = self.app.test_client()

    def test_default_parameter(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Int(missing=10))
        def test(param1):
            self.assertEqual(param1, 10)
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)

    def test_invalid_parameter(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Int())
        def test(param1):
            pass
        response = self.client.get('/resource?param1=a')
        self.assertEqual(response.status_code, 400)

    def test_required_parameter(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(required=True))
        def test(param1):
            pass
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 400)

    def test_validate_successfully_parameter(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(validate=lambda val: 1 <= val <= 10))
        def test(param1):
            self.assertEqual(param1, 5)
        response = self.client.get('/resource?param1=5')
        self.assertEqual(response.status_code, 204)

    def test_validate_broken_parameter(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(validate=lambda val: 1 <= val <= 10))
        def test(param1):
            pass
        response = self.client.get('/resource?param1=11')
        self.assertEqual(response.status_code, 400)

    def test_parameter_name_different_from_argument_name(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param2', fields.Integer(attribute='param1'))
        def test(param2):
            self.assertEqual(param2, 10)
        response = self.client.get('/resource?param1=10')
        self.assertEqual(response.status_code, 204)

    def test_multiple_parameter(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.List(fields.Int()))
        def test(param1):
            self.assertEqual(param1[0], 10)
            self.assertEqual(param1[1], 20)
        response = self.client.get('/resource?param1=10&param1=20')
        self.assertEqual(response.status_code, 204)

