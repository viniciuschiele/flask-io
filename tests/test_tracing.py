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
from unittest import TestCase


class TestTrace(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.io.tracer.enabled = True
        self.client = self.app.test_client()

    def test_default(self):
        @self.app.route('/resource')
        def test():
            pass

        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)

    def test_handlers(self):
        self.steps = 0

        @self.app.route('/resource')
        def test():
            pass

        @self.io.trace_inspect()
        def trace_inspect(data):
            self.steps += 1
            data['entry'] = 'value'

        @self.io.trace_emit()
        def trace_emit(data):
            self.steps += 1
            self.assertEqual(data['entry'], 'value')

        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.steps, 2)

    def test_exception(self):
        self.error = None

        @self.app.route('/resource')
        def test():
            raise Exception('error')

        @self.io.trace_inspect()
        def trace_inspect(data):
            self.error = data['error']

        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 500)
        self.assertIsNotNone(self.error)
