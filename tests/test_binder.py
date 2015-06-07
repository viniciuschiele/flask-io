from flask import Flask
from flask_binding import Binder
from flask_binding import EvaluationError
from flask_binding import FromQuery
from unittest import TestCase


class TestInteger(TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_valid_value(self):
        with self.app.test_request_context('/resource?param1=10', method='get'):
            args = Binder.bind({'param1': FromQuery(int)})
            self.assertEqual(args, {'param1': 10})

    def test_invalid_value(self):
        with self.app.test_request_context('/resource?param1=a', method='post'):
            self.assertRaises(EvaluationError, Binder.bind, {'param1': FromQuery(int)})

    def test_custom_name(self):
        with self.app.test_request_context('/resource?param2=1', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int, name='param2')}), {'param1': 1})

    def test_default_value(self):
        with self.app.test_request_context('/resource', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int, default=2)}), {'param1': 2})

    def test_missing_parameter(self):
        with self.app.test_request_context('/resource', method='post'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int)}), {'param1': None})

    def test_empty_parameter(self):
        with self.app.test_request_context('/resource?param1=', method='get'):
            self.assertRaises(EvaluationError, Binder.bind, {'param1': FromQuery(int)})

    def test_missing_required_parameter(self):
        with self.app.test_request_context('/resource', method='post'):
            self.assertRaises(EvaluationError, Binder.bind, {'param1': FromQuery(int, required=True)})

    def test_empty_required_parameter(self):
        with self.app.test_request_context('/resource?param1=', method='get'):
            self.assertRaises(EvaluationError, Binder.bind, {'param1': FromQuery(int, required=True)})

    def test_multiple_parameters(self):
        with self.app.test_request_context('/resource?param1=1&param1=2', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int, multiple=True)}), {'param1': [1, 2]})

    def test_invalid_multiple_parameters(self):
        with self.app.test_request_context('/resource?param1=1&param1=a', method='get'):
            self.assertRaises(EvaluationError, Binder.bind, {'param1': FromQuery(int, multiple=True)})

    def test_missing_multiple_parameters(self):
        with self.app.test_request_context('/resource', method='get'):
            self.assertEqual(Binder.bind({'param1': FromQuery(int)}), {'param1': None})

    def test_missing_required_multiple_parameters(self):
        with self.app.test_request_context('/resource', method='get'):
            self.assertRaises(EvaluationError, Binder.bind, {'param1': FromQuery(int, multiple=True, required=True)})
