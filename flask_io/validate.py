"""
Custom Validator classes that extend marshmallow Validator class.

All validators from marshmallow has been imported here to allow the user import them from the flask-io.
"""

import string

from marshmallow.validate import *


class Complexity(Validator):
    """
    A validator that allows to validate a str in several ways.

    The code below was inspired by django-password library.
    https://github.com/dstufft/django-passwords/blob/master/passwords/validators.py
    """

    # this has been added to prevent an issue with unit test.
    error = None

    def __init__(self, upper=0, lower=0, letters=0, digits=0, special=0, special_chars=None):
        """
        Initializes a new instance of `Complexity`.

        :param int upper: Number of uppercase letters that the str must have.
        :param int lower: Number of lowercase letters that the str must have.
        :param int letters: Number of letters that the str must have.
        :param int letters: Number of special characters that the str must have.
        :param str special_chars: List of special characters allowed.
        """
        self.upper = upper
        self.lower = lower
        self.letters = letters
        self.digits = digits
        self.special = special
        self.special_chars = special_chars or string.punctuation

    def __call__(self, value):
        uppercase, lowercase, letters = set(), set(), set()
        digits, special = set(), set()

        for character in value:
            if character.isupper():
                uppercase.add(character)
                letters.add(character)
            elif character.islower():
                lowercase.add(character)
                letters.add(character)
            elif character.isdigit():
                digits.add(character)
            elif character in self.special_chars:
                special.add(character)
            else:
                raise ValidationError('Only %s are allowed as special characters' % self.special_chars)

        if len(uppercase) < self.upper:
            raise ValidationError('Must contain %s or more unique uppercase characters' % self.upper)

        if len(lowercase) < self.lower:
            raise ValidationError('Must contain %s or more unique lowercase characters' % self.lower)

        if len(letters) < self.letters:
            raise ValidationError('Must contain %s or more unique lowercase letters' % self.letters)

        if len(digits) < self.digits:
            raise ValidationError('Must contain %s or more unique digits' % self.digits)

        if len(special) < self.special:
            raise ValidationError('Must contain %s or more unique special characters' % self.special)

        return value


class MACAddress(Validator):
    """
    Validate a MAC Address.
    """

    MAC_REGEX = re.compile('[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$', re.IGNORECASE)

    default_message = 'Not a valid MAC Address.'

    def __init__(self, error=None):
        """
        Initialize a new instance of MACAddress class.
        :param str error: Error message to raise in case of a validation error.
            Can be interpolated with `{input}`.
        """
        self.error = error or self.default_message

    def __call__(self, value):
        message = self._format_error(value)
        if not value:
            raise ValidationError(message)

        if not self.MAC_REGEX.search(value):
            raise ValidationError(message)

        return value

    def _format_error(self, value):
        return self.error.format(input=value)
