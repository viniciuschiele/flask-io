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

from marshmallow import Schema, fields
from .errors import Error


class ErrorResult(object):
    def __init__(self, code, errors):
        self.code = code

        if isinstance(errors, str):
            self.errors = [Error(errors)]
        elif isinstance(errors, list):
            self.errors = errors
        else:
            self.errors = [errors]

        self.message = self.errors[0].message


class ErrorSchema(Schema):
    code = fields.String()
    message = fields.String()
    location = fields.String()
    field = fields.String()


class ErrorResultSchema(Schema):
    code = fields.Integer()
    message = fields.String()
    errors = fields.Nested(ErrorSchema, many=True)
