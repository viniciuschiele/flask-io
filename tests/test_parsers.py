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


from datetime import datetime
from flask_io.parsers import parse_bool, parse_datetime, parse_primitive
from unittest import TestCase


class TestBoolean(TestCase):
    def test_valid_value(self):
        self.assertEqual(parse_bool(bool, 'true'), True)

    def test_invalid_value(self):
        self.assertRaises(ValueError, parse_bool, bool, 'abc')

    def test_empty_value(self):
        self.assertRaises(ValueError, parse_bool, bool, '')

    def test_none_value(self):
        self.assertRaises(TypeError, parse_bool, bool, None)


class TestInteger(TestCase):
    def test_valid_value(self):
        self.assertEqual(parse_primitive(int, '10'), 10)

    def test_invalid_value(self):
        self.assertRaises(ValueError, parse_primitive, int, 'abc')

    def test_empty_value(self):
        self.assertRaises(ValueError, parse_primitive, int, '')

    def test_none_value(self):
        self.assertRaises(TypeError, parse_primitive, int, None)


class TestFloat(TestCase):
    def test_valid_value(self):
        self.assertEqual(parse_primitive(float, '10.2'), 10.2)

    def test_invalid_value(self):
        self.assertRaises(ValueError, parse_primitive, float, 'abc')

    def test_empty_value(self):
        self.assertRaises(ValueError, parse_primitive, float, '')

    def test_none_value(self):
        self.assertRaises(TypeError, parse_primitive, float, None)


class TestDateTime(TestCase):
    def test_valid_value(self):
        self.assertEqual(parse_datetime(datetime, '2015-06-30'), datetime(2015, 6, 30))
        self.assertEqual(parse_datetime(datetime, '2015-06-30T14:01:30'), datetime(2015, 6, 30, 14, 1, 30))

    def test_invalid_value(self):
        self.assertRaises(ValueError, parse_datetime, datetime, 'abc')

    def test_empty_value(self):
        self.assertRaises(ValueError, parse_datetime, datetime, '')

    def test_none_value(self):
        self.assertRaises(TypeError, parse_datetime, datetime, None)
