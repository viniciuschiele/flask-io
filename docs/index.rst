.. flask-io documentation master file

********************************************
Flask-IO: Flask endpoints like functions
********************************************

Release v\ |version|. (:ref:`Changelog <changelog>`)

**Flask-IO** is a library for converting Flask request into function parameters and Flask response from the function's return.
Flask-IO uses under the hood the library `marshmallow <https://pypi.python.org/pypi/marshmallow>`_ to convert Flask request to native Python data types and native Python data types to Flask response.

.. code-block:: python

    from flask import Flask
    from flask_io import FlaskIO, fields, post_load, validate

    app = Flask(__name__)
    io = FlaskIO(app)

    class User(object):
        def __init__(self, **kwargs):
            self.username = kwargs.get('username')
            self.password = kwargs.get('password')
            self.first_name = kwargs.get('first_name')

    class UserSchema(Schema):
        username = fields.String(required=True)
        password = fields.String(load_only=True, validate=validate.Length(min=6))
        first_name = fields.String()

        def make_object(data)
            return User(**data)

    @app.route('/users', methods=['POST'])
    @io.from_body('user', UserSchema)
    @io.marshal_with(UserSchema)
    def add_user(user):
        # ... add the user to the database
        return user


Guide
=====

.. toctree::
    :maxdepth: 2

    install
    quickstart
