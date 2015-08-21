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

from marshmallow import fields, Schema
from marshmallow.utils import missing
from uuid import uuid4


class ActionContext(object):
    def __init__(self, func_name):
        self.func_name = func_name
        self.params = []
        self.__input_schema = None
        self.output_schema = None
        self.output_envelope = None
        self.trace_enabled = False

    @property
    def input_schema(self):
        if not self.__input_schema:
            self.__input_schema = self.__build_input_schema()
        return self.__input_schema

    def add_parameter(self, param_name, field_or_schema, location):
        field_or_schema = field_or_schema or fields.Raw()

        if isinstance(field_or_schema, fields.Field):
            if not field_or_schema.required:
                field_or_schema.allow_none = True
                if field_or_schema.missing == missing:
                    field_or_schema.missing = None

            if field_or_schema.attribute:
                old_param_name = param_name
                param_name = field_or_schema.attribute
                field_or_schema.attribute = old_param_name

        self.params.append((param_name, field_or_schema, location))

    def __build_input_schema(self):
        attrs = {}
        for param_name, field_or_schema, _ in self.params:
            if isinstance(field_or_schema, Schema):
                field_or_schema = fields.Nested(field_or_schema, required=True)
            attrs[param_name] = field_or_schema
        return type('IOSchema' + str(uuid4()), (Schema,), attrs)()
