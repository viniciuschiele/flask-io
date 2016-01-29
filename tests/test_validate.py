from flask_io.validate import Complexity, MACAddress, ValidationError
from unittest import TestCase


class TestComplexity(TestCase):
    def test_upper(self):
        validator = Complexity(upper=1)
        self.assertEqual(validator('Hello'), 'Hello')

        validator = Complexity(upper=2)
        self.assertEqual(validator('HeLlo'), 'HeLlo')

        validator = Complexity(upper=1)
        self.assertRaises(ValidationError, validator, 'hello')

        validator = Complexity(upper=2)
        self.assertRaises(ValidationError, validator, 'Hello')

    def test_lower(self):
        validator = Complexity(lower=1)
        self.assertEqual(validator('hELLO'), 'hELLO')

        validator = Complexity(lower=2)
        self.assertEqual(validator('hELlO'), 'hELlO')

        validator = Complexity(lower=1)
        self.assertRaises(ValidationError, validator, 'HELLO')

        validator = Complexity(lower=2)
        self.assertRaises(ValidationError, validator, 'hELLO')

    def test_letters(self):
        validator = Complexity(letters=1)
        self.assertEqual(validator('123s'), '123s')

        validator = Complexity(letters=2)
        self.assertEqual(validator('i23s'), 'i23s')

        validator = Complexity(letters=1)
        self.assertRaises(ValidationError, validator, '1234')

        validator = Complexity(letters=2)
        self.assertRaises(ValidationError, validator, '123s')

    def test_digits(self):
        validator = Complexity(digits=1)
        self.assertEqual(validator('hell0'), 'hell0')

        validator = Complexity(digits=2)
        self.assertEqual(validator('he1l0'), 'he1l0')

        validator = Complexity(digits=1)
        self.assertRaises(ValidationError, validator, 'hello')

        validator = Complexity(digits=2)
        self.assertRaises(ValidationError, validator, 'hell0')

    def test_special(self):
        validator = Complexity(special=1)
        self.assertEqual(validator('hell@'), 'hell@')

        validator = Complexity(special=2)
        self.assertEqual(validator('he?l@'), 'he?l@')

        validator = Complexity(special=1)
        self.assertRaises(ValidationError, validator, 'hello')

        validator = Complexity(special=2)
        self.assertRaises(ValidationError, validator, 'hell@')


class TestMACAddress(TestCase):
    def test_valid_mac(self):
        validator = MACAddress()
        self.assertEqual(validator('00-15-E9-2B-99-3C'), '00-15-E9-2B-99-3C')
        self.assertEqual(validator('00:15:E9:2B:99:3C'), '00:15:E9:2B:99:3C')

    def test_invalid_mac(self):
        validator = MACAddress()
        self.assertRaises(ValidationError, validator, '00-15-E9-2B-99-3')
        self.assertRaises(ValidationError, validator, '0015E92B993C')
