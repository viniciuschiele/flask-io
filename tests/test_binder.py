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
from flask_binding import Binder
from flask_binding import FromBody
from flask_binding import FromQuery
from flask_binding.errors import InvalidArgumentError
from flask_binding.errors import RequiredArgumentError
from unittest import TestCase


class TestInteger(TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_valid_value(self):
        with self.app.test_request_context('/resource?param1=10', method='get'):
            args = Binder.bind({'param1': FromQuery(int)})
            self.assertEqual(args, {'param1': 10})

    def test_invalid_value(self):
        with self.app.test_request_context('/resource?param1=a', method='post'):
            self.assertRaises(InvalidArgumentError, Binder.bind, {'param1': FromQuery(int)})

    def test_custom_name(self):
        with self.app.test_request_context('/resource?param2=1', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int, name='param2')}), {'param1': 1})

    def test_default_value(self):
        with self.app.test_request_context('/resource', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int, default=2)}), {'param1': 2})

    def test_missing_parameter(self):
        with self.app.test_request_context('/resource', method='post'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int)}), {'param1': None})

    def test_empty_parameter(self):
        with self.app.test_request_context('/resource?param1=', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int)}), {'param1': None})

    def test_missing_required_parameter(self):
        with self.app.test_request_context('/resource', method='post'):
            self.assertRaises(RequiredArgumentError, Binder.bind, {'param1': FromQuery(int, required=True)})

    def test_empty_required_parameter(self):
        with self.app.test_request_context('/resource?param1=', method='get'):
            self.assertRaises(RequiredArgumentError, Binder.bind, {'param1': FromQuery(int, required=True)})

    def test_multiple_parameters(self):
        with self.app.test_request_context('/resource?param1=1&param1=2', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int, multiple=True)}), {'param1': [1, 2]})

    def test_invalid_multiple_parameters(self):
        with self.app.test_request_context('/resource?param1=1&param1=a', method='get'):
            self.assertRaises(InvalidArgumentError, Binder.bind, {'param1': FromQuery(int, multiple=True)})

    def test_missing_multiple_parameters(self):
        with self.app.test_request_context('/resource', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int)}), {'param1': None})

    def test_missing_required_multiple_parameters(self):
        with self.app.test_request_context('/resource', method='get'):
            self.assertRaises(RequiredArgumentError, Binder.bind,
                              {'param1': FromQuery(int, multiple=True, required=True)})

    def test_body_as_json(self):
        data = {
            'key1': 1,
            'key2': '2'
        }
        with self.app.test_request_context('/resource', method='post',
                                           data=json.dumps(data),
                                           content_type='application/json'):
            self.assertEqual(Binder.bind({'param1': FromBody(dict)}), {'param1': data})

    def test_invalid_body_as_json(self):
        with self.app.test_request_context('/resource', method='post',
                                           data='abc',
                                           content_type='application/json'):
            self.assertRaises(InvalidArgumentError, Binder.bind, {'param1': FromBody(dict)})

    def test_missing_body_as_json(self):
        with self.app.test_request_context('/resource', method='post', content_type='application/json'):
            self.assertEqual(Binder.bind({'param1': FromBody(dict)}), {'param1': None})

    def test_missing_required_body_as_json(self):
        with self.app.test_request_context('/resource', method='post', content_type='application/json'):
            self.assertRaises(RequiredArgumentError, Binder.bind, {'param1': FromBody(dict, required=True)})
