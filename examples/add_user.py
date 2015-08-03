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
from flask_io import fields, Schema

app = Flask(__name__)

io = FlaskIO()
io.init_app(app)


class User(object):
    def __init__(self, username):
        self.username = username


class UserSchema(Schema):
    username = fields.Integer()

    def make_object(self, data):
        return User(**data)


@app.route('/users', methods=['POST'])
@io.from_body('user', UserSchema)
@io.marshal_with(UserSchema)
def add_user(user):
    return user

if __name__ == '__main__':
    app.run()
