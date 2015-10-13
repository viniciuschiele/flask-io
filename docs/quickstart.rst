.. _quickstart:

Quickstart
============

Request parsing
----------------
Arguments can be retrieved using the following decorators:

 * from_query
 * from_form
 * from_header
 * from_cookie
 * from_body

.. code-block:: python

    from flask import Flask
    from flask_io import FlaskIO
    from marshmallow import fields

    app = Flask(__name__)
    io = FlaskIO(app)

    @app.route('/')
    @io.from_query('username', fields.String(required=True))
    def does_username_exist(username):
        return False

Each parameter accepts either a `Field <http://marshmallow.readthedocs.org/en/latest/api_reference.html#module-marshmallow.fields>`_ or `Schema <http://marshmallow.readthedocs.org/en/latest/api_reference.html#schema>`_ to parse the arguments, the full documentation about those classes can be found `here <http://marshmallow.readthedocs.org>`_.

Output fields
----------------
Any object can be returned straight from the your function, Flask-IO will serialize the object for you.
Complex object needs a `Schema <http://marshmallow.readthedocs.org/en/latest/api_reference.html#schema>`_ specified to be serialized, to specify a `Schema <http://marshmallow.readthedocs.org/en/latest/api_reference.html#schema>`_ you can use the decorator `marshal_with`

.. code-block:: python

    from flask import Flask
    from flask_io import FlaskIO
    from marshmallow import fields

    app = Flask(__name__)
    io = FlaskIO(app)

    class UserSchema(Schema):
        username = fields.String()

    @app.route('/users/<username>')
    @io.marshal_with(UserSchema)
    def get_user(username):
        return User(username=username)

Python's built-in types can be serialized without a Schema, for example, it is possible to return a dict` without a Schema specified.


.. code-block:: python

    from flask import Flask
    from flask_io import FlaskIO

    app = Flask(__name__)
    io = FlaskIO(app)

    @app.route('/users/<username>')
    def get_user(username):
        return dict(username=username)

A function does not even need to return an object, Flask-IO will return a response with status code 204 in this case.

.. code-block:: python

    from flask import Flask
    from flask_io import FlaskIO

    app = Flask(__name__)
    io = FlaskIO(app)

    @app.route('/users/<username>', methods=['DELETE'])
    def delete_user(username):
        pass


Error handling
----------------
By default any error is serialized following the same structure.


.. code-block:: python

    {
        errors: [
            {
                "message": "User already exists: john123",
                "code": "user_already_exists",
                "field": "username",
                "location": "body"
            }
        ]
    }

The error structure supports more than one error at the same time, usually argument validation returns more than one error.

Structure details:

 * **message** is always present, it describes the error itself.
 * **code** specifies a custom error code, it might be specified or not, it is up to you.
 * **field** specifies the field name which is invalid.
 * **location** specifies the location from where the error comes. Possible values are: `query`, `form`, `header`, `cookie` and `body`.

.. code-block:: python

    from flask import Flask
    from flask_io import FlaskIO

    app = Flask(__name__)
    io = FlaskIO(app)

    class UserSchema(Schema):
        username = fields.String(required=True, validate=validate.Length(min=6))

    @app.route('/users>')
    @io.from_body('user', UserSchema)
    def add_user(user):
        pass

.. code-block:: python

    curl -X POST -H "Content-Type: application/json" http://localhost:5000/users -d '{"username":"john"}'

    >>

    {
        errors: [
            {
                "message": "Shorter than minimum length 6.",
                "field": "username",
                "location": "body"
            }
        ]
    }
