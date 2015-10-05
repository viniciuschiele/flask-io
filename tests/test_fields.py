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

from marshmallow.validate import ValidationError
from flask_io.fields_ext import Password
from unittest import TestCase


class TestPassword(TestCase):
    def test_default_settings(self):
        field = Password()

        self.assertEqual('Pa4sw@rd', field.deserialize('Pa4sw@rd'))
        self.assertRaises(ValidationError, field.deserialize, 'pa4sw@rd')
