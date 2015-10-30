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


class TestString(TestCase):
    def test_allow_empty(self):
        field = fields.String()
        self.assertEqual('', field.deserialize(''))

        field = fields.String(allow_empty=False)
        self.assertRaises(ValidationError, field.deserialize, '')

    def test_none_if_empty(self):
        field = fields.String(none_if_empty=True)
        self.assertRaises(ValidationError, field.deserialize, '')

        field = fields.String(allow_none=True, none_if_empty=True)
        self.assertIsNone(field.deserialize(''))

    def test_strip(self):
        field = fields.String(strip=True)
        self.assertEqual('b', field.deserialize(' b '))

    def test_only_numeric(self):
        field = fields.String(only_numeric=True)
        self.assertEqual('12345', field.deserialize('12345'))
        self.assertRaises(ValidationError, field.deserialize, 'abcde')
