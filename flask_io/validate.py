# The code below was inspired by django-password library.
# https://github.com/dstufft/django-passwords/blob/master/passwords/validators.py

import string

from marshmallow.validate import *


class Complexity(Validator):
    error = None

    def __init__(self, upper=0, lower=0, letters=0, digits=0, special=0, special_chars=None):
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
