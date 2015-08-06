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

from flask import Flask
from flask_io import FlaskIO
from flask_io import Error, fields, Schema
from datetime import datetime
from uuid import uuid4

app = Flask(__name__)

io = FlaskIO()
io.init_app(app)


class User(object):
    def __init__(self, id, username, first_name, last_name, enabled):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.enabled = enabled
        self.created_at = None


class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    username = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)
    created_at = fields.DateTime(dump_only=True)

    def make_object(self, data):
        return User(**data)


class UpdateUserSchema(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Email(required=True)
    enabled = fields.Boolean(required=True)

    def make_object(self, data):
        return User(**data)


class PatchUserSchema(Schema):
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()


store = dict()


@app.route('/users', methods=['POST'])
@io.from_body('user', UserSchema)
@io.marshal_with(UserSchema)
def add_user(user):
    user.id = str(uuid4())
    user.created_at = datetime.now()
    store[user.id] = user
    return user


@app.route('/users')
@io.from_query('username', fields.String(missing=''))
@io.from_query('max_results', fields.Integer(missing=10))
@io.marshal_with(UserSchema)
def get_users(username, max_results):
    users = list(store.values())

    if username:
        users = [user for user in users if user.username.find(username) > -1]

    return users[:max_results]


@app.route('/users/<user_id>', methods=['POST'])
@io.from_body('new_user', UpdateUserSchema)
@io.marshal_with(UserSchema)
def update_user(user_id, new_user):
    user = store.get(user_id)

    if not user:
        return io.not_found(Error('User not found: ' + user_id))

    user.first_name = new_user.first_name
    user.last_name = new_user.last_name
    user.email = new_user.email

    return user


@app.route('/users/<user_id>', methods=['PATCH'])
@io.from_body('new_user', PatchUserSchema)
@io.marshal_with(UserSchema)
def patch_user(user_id, new_user):
    user = store.get(user_id)

    if not user:
        return io.not_found(Error('User not found: ' + user_id))

    user.first_name = new_user.get('first_name', user.first_name)
    user.last_name = new_user.get('last_name', user.last_name)
    user.email = new_user.get('email', user.email)

    return user

if __name__ == '__main__':
    app.run()
