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

from marshmallow import fields, validate


class Enum(fields.Field):
    """A field that provides a set of enumerated values which an attribute must be constrained to."""

    def __init__(self, enum_type, member_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_type = enum_type

        if member_type:
            self.member_type = member_type
        else:
            self.member_type = type(list(self.enum_type)[0].value)

        self.validators.insert(0, validate.OneOf([v.value for v in self.enum_type]))

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
