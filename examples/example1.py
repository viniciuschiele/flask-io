from flask import Flask
from flask import jsonify
from flask_binding import bind
from flask_binding import FromQuery
from flask_binding.errors import InvalidArgumentError
from flask_binding.errors import RequiredArgumentError

app = Flask(__name__)
app.debug = True

@app.route('/people')
@bind({'name': FromQuery(str),
       'max_results': FromQuery(int, default=10)})
def list_people(name, max_results):
    people = []

    for i in range(max_results):
        people.append({
            'name': 'person' + str(i)
        })

    if name:
        people = [person for person in people if person.get('name').startswith(name)]

    return jsonify(people=people)

@app.errorhandler(InvalidArgumentError)
def error_handler(error):
    response = jsonify(error_message='Argument %s is invalid' % error.arg_name)
    response.status_code = 400
    return response

@app.errorhandler(RequiredArgumentError)
def error_handler(error):
    response = jsonify(error_message='Argument %s is missing' % error.arg_name)
    response.status_code = 400
    return response

if __name__ == '__main__':
    app.run()
