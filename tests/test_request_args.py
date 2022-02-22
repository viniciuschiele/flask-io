from flask import Flask
from flask_io import FlaskIO, fields
from unittest import TestCase


class TestRequestArgs(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.client = self.app.test_client()

    def test_missing_value(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Int())
        def test(param1):
            self.assertEqual(param1, None)
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)

    def test_missing_required_value(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(required=True))
        def test(param1):
            pass
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 400)

    def test_empty_value(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Int())
        def test(param1):
            self.assertEqual(param1, None)
        response = self.client.get('/resource?param1=')
        self.assertEqual(response.status_code, 204)

    def test_empty_required_value(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(required=True))
        def test(param1):
            pass
        response = self.client.get('/resource?param1=')
        self.assertEqual(response.status_code, 400)

    def test_default_value(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Int(load_default=10))
        def test(param1):
            self.assertEqual(param1, 10)
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)

    def test_invalid_value(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Int())
        def test(param1):
            pass
        response = self.client.get('/resource?param1=a')
        self.assertEqual(response.status_code, 400)

    def test_success_validate(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(validate=lambda val: 1 <= val <= 10))
        def test(param1):
            self.assertEqual(param1, 5)
        response = self.client.get('/resource?param1=5')
        self.assertEqual(response.status_code, 204)

    def test_fail_validate(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.Integer(validate=lambda val: 1 <= val <= 10))
        def test(param1):
            pass
        response = self.client.get('/resource?param1=11')
        self.assertEqual(response.status_code, 400)

    def test_data_key(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param2', fields.Integer(data_key='param1'))
        def test(param2):
            self.assertEqual(param2, 10)
        response = self.client.get('/resource?param1=10')
        self.assertEqual(response.status_code, 204)

    def test_list(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.List(fields.Int()))
        def test(param1):
            self.assertEqual(param1[0], 10)
            self.assertEqual(param1[1], 20)
        response = self.client.get('/resource?param1=10&param1=20')
        self.assertEqual(response.status_code, 204)

    def test_missing_required_list(self):
        @self.app.route('/resource', methods=['GET'])
        @self.io.from_query('param1', fields.List(fields.Int(), required=True))
        def test(param1):
            pass
        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 400)
