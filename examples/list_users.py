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
from flask_binding import bind
from flask_binding import FromQuery
from flask_binding.errors import InvalidArgumentError
from flask_binding.errors import RequiredArgumentError

app = Flask(__name__)
app.debug = True

@app.route('/users')
@bind({'name': FromQuery(str),
       'max_results': FromQuery(int, default=10)})
def list_users(name, max_results):
    users = []

    for i in range(max_results):
        users.append({
            'name': 'user' + str(i)
        })

    if name:
        users = [user for user in users if user.get('name').startswith(name)]

    return jsonify(users=users)

@app.errorhandler(InvalidArgumentError)
def invalid_argument_handler(error):
    response = jsonify(error_message='Argument %s is invalid' % error.arg_name)
    response.status_code = 400
    return response

@app.errorhandler(RequiredArgumentError)
def required_argument_handler(error):
    response = jsonify(error_message='Argument %s is missing' % error.arg_name)
    response.status_code = 400
    return response

if __name__ == '__main__':
    app.run()
