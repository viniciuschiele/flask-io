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
from flask import jsonify
from flask_io import FlaskIO
from flask_io.errors import ValidationError

app = Flask(__name__)
app.debug = True

io = FlaskIO()
io.init_app(app)


@app.route('/users')
@io.from_query('name', str, required=True)
@io.from_query('max_results', int, default=10)
@io.render()
def list_users(name, max_results):
    users = []

    for i in range(max_results):
        users.append({
            'name': 'user' + str(i)
        })

    if name:
        users = [user for user in users if user.get('name').find(name) > -1]

    return jsonify(users=users)


@app.errorhandler(ValidationError)
def validation_handler(error):
    response = jsonify(error_message=error.message)
    response.status_code = 400
    return response


if __name__ == '__main__':
    app.run()
