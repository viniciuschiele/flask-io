from flask import Flask
from flask_io import FlaskIO
from unittest import TestCase


class TestTrace(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.io = FlaskIO()
        self.io.init_app(self.app)
        self.io.tracer.enabled = True
        self.client = self.app.test_client()

    def test_default(self):
        @self.app.route('/resource')
        def test():
            pass

        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)

    def test_handlers(self):
        self.steps = 0

        @self.app.route('/resource')
        def test():
            pass

        @self.io.trace_inspect()
        def trace_inspect(data):
            self.steps += 1
            data['entry'] = 'value'

        @self.io.trace_emit()
        def trace_emit(data):
            self.steps += 1
            self.assertEqual(data['entry'], 'value')

        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.steps, 2)

    def test_exception(self):
        self.error = None

        @self.app.route('/resource')
        def test():
            raise Exception('expected error in test_exception')

        @self.io.trace_inspect()
        def trace_inspect(data):
            self.error = data['error']

        response = self.client.get('/resource')
        self.assertEqual(response.status_code, 500)
        self.assertIsNotNone(self.error)

    def test_filter_endpoints(self):
        self.io.tracer.add_filter(endpoints=['test2'])
        self.steps = 0

        @self.app.route('/test1')
        def test1():
            pass

        @self.app.route('/test2')
        def test2():
            pass

        @self.io.trace_emit()
        def trace_emit(data):
            self.steps += 1

        response = self.client.get('/test1')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/test2')
        self.assertEqual(response.status_code, 204)

        self.assertEqual(self.steps, 1)

    def test_filter_methods(self):
        self.io.tracer.add_filter(['POST'])
        self.steps = 0

        @self.app.route('/get', methods=['GET'])
        def get_test():
            pass

        @self.app.route('/post', methods=['POST'])
        def post_test():
            pass

        @self.io.trace_emit()
        def trace_emit(data):
            self.steps += 1

        response = self.client.get('/get')
        self.assertEqual(response.status_code, 204)

        response = self.client.post('/post')
        self.assertEqual(response.status_code, 204)

        self.assertEqual(self.steps, 1)
