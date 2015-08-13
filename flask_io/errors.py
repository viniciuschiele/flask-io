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

from marshmallow import fields, Schema, post_dump


class Error(object):
    def __init__(self, message, reason=None, location=None, field=None):
        self.message = message
        self.reason = reason
        self.location = location
        self.field = field


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
    message = fields.String()
    reason = fields.String()
    location = fields.String()
    field = fields.String()

    @post_dump
    def remove_none_fields(self, data):
        if not data.get('message'):
            data.pop('message')

        if not data.get('reason'):
            data.pop('reason')

        if not data.get('location'):
            data.pop('location')

        if not data.get('field'):
            data.pop('field')

        return data


class ErrorResultSchema(Schema):
    code = fields.Integer()
    message = fields.String()
    errors = fields.Nested(ErrorSchema, many=True)
