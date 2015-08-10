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
from flask_io import FlaskIO, Error, fields
from datetime import datetime
from example.schemas import UserSchema, PatchUserSchema, UpdateUserSchema

app = Flask(__name__)

io = FlaskIO()
io.init_app(app)

store = dict()


@app.route('/users', methods=['POST'])
@io.from_body('user', UserSchema)
@io.marshal_with(UserSchema)
def add_user(user):
    if store.get(user.username):
        return io.conflict('User already exists: ' + user.username)

    user.created_at = datetime.now()
    store[user.username] = user
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


@app.route('/users/<username>', methods=['POST'])
@io.from_body('new_user', UpdateUserSchema)
@io.marshal_with(UserSchema)
def update_user(username, new_user):
    user = store.get(username)

    if not user:
        return io.not_found('User not found: ' + username)

    user.first_name = new_user.first_name
    user.last_name = new_user.last_name
    user.email = new_user.email

    return user


@app.route('/users/<username>', methods=['PATCH'])
@io.from_body('new_user', PatchUserSchema)
@io.marshal_with(UserSchema)
def patch_user(username, new_user):
    user = store.get(username)

    if not user:
        return io.not_found('User not found: ' + username)

    user.first_name = new_user.get('first_name', user.first_name)
    user.last_name = new_user.get('last_name', user.last_name)
    user.email = new_user.get('email', user.email)

    return user

if __name__ == '__main__':
    app.run()
