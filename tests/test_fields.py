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

from enum import Enum
from flask_io import fields
from flask_io.validate import ValidationError
from unittest import TestCase


class MyEnum(Enum):
    member1 = 1
    member2 = 2
    member3 = 3


class TestDelimitedList(TestCase):
    def test_serialize(self):
        field = fields.DelimitedList(fields.Integer)

        self.assertEqual(field.serialize('a', {'a': [1, 2, 3]}), '1,2,3')

    def test_deserialize(self):
        field = fields.DelimitedList(fields.Integer)

        self.assertEqual(field.deserialize('1,2, 3'), [1, 2, 3])


class TestEnum(TestCase):
    def test_serialize(self):
        field = fields.Enum(MyEnum)

        self.assertEqual(field.serialize('a', {'a': MyEnum.member2}), 2)

    def test_deserialize(self):
        field = fields.Enum(MyEnum)

        self.assertEqual(field.deserialize(2), MyEnum.member2)


class TestPassword(TestCase):
    def test_default_settings(self):
        field = fields.Password()

        self.assertEqual('Pa4sw@rd', field.deserialize('Pa4sw@rd'))
        self.assertRaises(ValidationError, field.deserialize, 'pa4sw@rd')
