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

from marshmallow import fields, post_load, Schema
from marshmallow.validate import Length
from .models import User


class UserSchema(Schema):
    username = fields.String(required=True, validate=Length(5, 30))
    first_name = fields.String(required=True, validate=Length(1, 50))
    last_name = fields.String(required=True, validate=Length(1, 50))
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_object(self, data):
        return User(**data)


class UpdateUserSchema(Schema):
    first_name = fields.String(required=True, validate=Length(1, 50))
    last_name = fields.String(required=True, validate=Length(1, 50))
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)

    @post_load
    def make_object(self, data):
        return User(**data)


class PatchUserSchema(Schema):
    first_name = fields.String(validate=Length(1, 50))
    last_name = fields.String(validate=Length(1, 50))
    email = fields.Email()
    enabled = fields.Boolean()
