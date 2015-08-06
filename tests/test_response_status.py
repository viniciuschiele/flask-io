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
from flask_io.errors import Error
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
