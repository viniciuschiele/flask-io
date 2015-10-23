"""
Custom Field classes that extend marshmallow Field class.

All fields from marshmallow has been imported here to allow the user import them from the flask-io.
"""

from marshmallow.fields import *
from marshmallow.validate import Length, OneOf
from .validate import Complexity


class DelimitedList(List):
    """
    A delimited list composed with another `Field` class that loads from a delimited string.
    """

    delimiter = ','

    def __init__(self, cls_or_instance, delimiter=None, **kwargs):
        """
        Initializes a new instance of `DelimitedList`.

        :param Field cls_or_instance: A field class or instance.
        :param str delimiter: Delimiter between values.
        """
        self.delimiter = delimiter or self.delimiter
        super().__init__(cls_or_instance, **kwargs)

    def _serialize(self, value, attr, obj):
        values = super()._serialize(value, attr, obj)
        return self.delimiter.join(format(v) for v in values)

    def _deserialize(self, value, attr, data):
        values = value.split(self.delimiter)
        return super()._deserialize(values, attr, data)


class Enum(Field):
    """
    A field that provides a set of enumerated values which an attribute must be constrained to.
    """

    def __init__(self, enum_type, *args, **kwargs):
        """
        Initializes a new instance of `Enum`.

        :param enum.Enum enum_type: A Python enum class.
        """

        super().__init__(*args, **kwargs)
        self.enum_type = enum_type
        self.__member_type = type(list(self.enum_type)[0].value)

        self.validators.append(OneOf([v.value for v in self.enum_type]))

    def _serialize(self, value, attr, obj):
        if type(value) is self.enum_type:
            return value.value
        if type(value) is not self.__member_type:
            value = self.__member_type(value)
        return self.enum_type(value).value

    def _deserialize(self, value, attr, data):
        if type(value) is self.enum_type:
            return value
        if type(value) is not self.__member_type:
            value = self.__member_type(value)
        return self.enum_type(value)

    def _validate(self, value):
        if type(value) is self.enum_type:
            super()._validate(value.value)
        else:
            super()._validate(value)


class Password(Field):
    """
    A password field used to validate strong passwords.
    """
    def __init__(self, upper=1, lower=1, letters=1, digits=1, special=1, special_chars=None, min_length=6, max_length=None, *args, **kwargs):
        """
        Initializes a new instance of `Password`.

        :param int upper: Number of uppercase letters that the password must have.
        :param int lower: Number of lowercase letters that the password must have.
        :param int letters: Number of letters that the password must have.
        :param int letters: Number of special characters that the password must have.
        :param str special_chars: List of special characters allowed.
        :param int min_length: Minimum of characters that the password must have.
        :param int max_length: Maximum of characters that the password must have.
        """
        super().__init__(*args, **kwargs)

        self.validators.append(Length(min_length, max_length))
        self.validators.append(Complexity(upper, lower, letters, digits, special, special_chars))
