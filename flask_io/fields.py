from marshmallow.fields import *
from marshmallow.validate import Length, OneOf
from .validate import Complexity


class DelimitedList(List):
    delimiter = ','

    def __init__(self, cls_or_instance, delimiter=None, **kwargs):
        self.delimiter = delimiter or self.delimiter
        super().__init__(cls_or_instance, **kwargs)

    def _serialize(self, value, attr, obj):
        values = super()._serialize(value, attr, obj)
        return self.delimiter.join(format(v) for v in values)

    def _deserialize(self, value, attr, data):
        values = value.split(self.delimiter)
        return super()._deserialize(values, attr, data)


class Enum(Field):
    """A field that provides a set of enumerated values which an attribute must be constrained to."""

    def __init__(self, enum_type, member_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_type = enum_type

        if member_type:
            self.member_type = member_type
        else:
            self.member_type = type(list(self.enum_type)[0].value)

        self.validators.append(OneOf([v.value for v in self.enum_type]))

    def _serialize(self, value, attr, obj):
        if type(value) is self.enum_type:
            return value.value
        if type(value) is not self.member_type:
            value = self.member_type(value)
        return self.enum_type(value).value

    def _deserialize(self, value, attr, data):
        if type(value) is self.enum_type:
            return value
        if type(value) is not self.member_type:
            value = self.member_type(value)
        return self.enum_type(value)

    def _validate(self, value):
        if type(value) is self.enum_type:
            super()._validate(value.value)
        else:
            super()._validate(value)


class Password(Field):
    def __init__(self, upper=1, lower=1, letters=1, digits=1, special=1, special_chars=None, min_length=6, max_length=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.validators.append(Length(min_length, max_length))
        self.validators.append(Complexity(upper, lower, letters, digits, special, special_chars))
