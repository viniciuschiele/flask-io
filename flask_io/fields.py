"""
Custom Field classes that extend marshmallow Field class.

All fields from marshmallow has been imported here to allow the user import them from the flask-io.
"""


from marshmallow import fields
from marshmallow.fields import *
from .validate import Complexity, Length


__all__ = [
    'DelimitedList',
    'Enum',
    'Password',
    'String'
]


for field_name in (field_name for field_name in fields.__all__ if field_name not in __all__):
    __all__.append(field_name)


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

        :param enum_type: A Python enum class.
        """

        super().__init__(*args, **kwargs)
        self.enum_type = enum_type
        self.__member_type = type(list(self.enum_type)[0].value)

    def _serialize(self, value, attr, obj):
        try:
            if type(value) is self.enum_type:
                return value.value
            if type(value) is not self.__member_type:
                value = self.__member_type(value)
            return self.enum_type(value).value
        except:
            self.fail('validator_failed')

    def _deserialize(self, value, attr, data):
        try:
            if type(value) is self.enum_type:
                return value
            if type(value) is not self.__member_type:
                value = self.__member_type(value)
            return self.enum_type(value)
        except:
            self.fail('validator_failed')


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


class String(fields.String):
    """
    Extends Marshmallow String Field to add new features.
    """

    allow_empty = True
    none_if_empty = False
    strip = False
    only_numeric = False
    upper = False

    default_error_messages = {
        'empty': 'Field may not be empty.',
        'only_numeric': 'Only numeric chars are allowed.'
    }

    def __init__(self, allow_empty=None, none_if_empty=None, strip=None, only_numeric=None, upper=None, *args, **kwargs):
        """
        Initializes a new instance of 'String'.

        :param bool allow_empty: Indicates whether the string can be empty ('').
        :param bool none_if_empty: Indicates whether the empty ('') should be considered 'None'.
        :param bool strip: Indicates whether the string should be trimmed.
        :param bool only_numeric: Indicates whether the string should have only numbers.
        :param bool upper: Indicates whether the string should be upper case.
        :return:
        """

        super().__init__(*args, **kwargs)
        self.allow_empty = self.allow_empty if allow_empty is None else allow_empty
        self.strip = self.strip if strip is None else strip
        self.none_if_empty = self.none_if_empty if none_if_empty is None else none_if_empty
        self.only_numeric = self.only_numeric if only_numeric is None else only_numeric
        self.upper = self.upper if upper is None else upper

    def deserialize(self, value, attr=None, data=None):
        if self.none_if_empty and value == '':
            value = None

        value = super().deserialize(value, attr, data)

        if value:
            if self.strip:
                value = value.strip()
            if self.upper:
                value = value.upper()

        return value

    def _validate(self, value):
        if not self.allow_empty and value == '':
            self.fail('empty')

        if self.none_if_empty and not self.allow_none and value is None:
            self.fail('null')

        if self.only_numeric and value and not value.isnumeric():
            self.fail('only_numeric')

        super()._validate(value)


class UUID(fields.UUID):
    """
    Extends Marshmallow UUID Field to add new features.
    """

    def __init__(self, as_text=False, *args, **kwargs):
        """
        Initializes a new instance of 'String'.

        :param bool as_text: Indicates whether the value should be converted to string.
        """
        super().__init__(*args, **kwargs)
        self.as_text = as_text

    def _deserialize(self, value, attr, data):
        value_as_uuid = super()._deserialize(value, attr, data)

        if self.as_text:
            return value

        return value_as_uuid


# Aliases
Str = String
