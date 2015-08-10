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

from flask_io import fields, Schema, ValidationError
from .models import User


def validate_username(value):
    if 8 > len(value) > 30:
        raise ValidationError('Username must be between 6 and 30 characters.')


def validate_first_name(value):
    if len(value) == 0:
        raise ValidationError('First name cannot be empty.')

    if len(value) > 50:
        raise ValidationError('First name cannot be greater than 50 characters.')


def validate_last_name(value):
    if len(value) == 0:
        raise ValidationError('Last name cannot be empty.')

    if len(value) > 50:
        raise ValidationError('Last name cannot be greater than 50 characters.')


class UserSchema(Schema):
    username = fields.String(required=True, validate=validate_username)
    first_name = fields.String(required=True, validate=validate_first_name)
    last_name = fields.String(required=True, validate=validate_last_name)
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)
    created_at = fields.DateTime(dump_only=True)

    def make_object(self, data):
        return User(**data)


class UpdateUserSchema(Schema):
    first_name = fields.String(required=True, validate=validate_first_name)
    last_name = fields.String(required=True, validate=validate_last_name)
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)

    def make_object(self, data):
        return User(**data)


class PatchUserSchema(Schema):
    first_name = fields.String(validate=validate_first_name)
    last_name = fields.String(validate=validate_last_name)
    email = fields.Email()
    enabled = fields.Boolean()
