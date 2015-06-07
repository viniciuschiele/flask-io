from werkzeug.datastructures import ImmutableMultiDict
from flask_binding.binder import BindingContext
from flask_binding.binders import PrimitiveBinder
from unittest import TestCase


class TestInteger(TestCase):
    def setUp(self):
        self.binder = PrimitiveBinder()

    def test_valid_value(self):
        context = BindingContext(int, 'param1', {'param1': 10})
        self.assertEqual(self.binder.bind(context), 10)

    def test_invalid_value(self):
        context = BindingContext(int, 'param1', {'param1': 'a'})
        self.assertRaises(Exception, self.binder.bind, context)

    def test_empty_value(self):
        context = BindingContext(int, 'param1', {'param1': ''})
        self.assertRaises(Exception, self.binder.bind, context)

    def test_missing_argument(self):
        context = BindingContext(int, 'param1', {'param2': 1})
        self.assertEqual(self.binder.bind(context), None)

    def test_multiple_parameters(self):
        params = ImmutableMultiDict([('param1', 1), ('param1', 2)])
        context = BindingContext(int, 'param1', params, multiple=True)
        self.assertEqual(self.binder.bind(context), [1, 2])

    def test_invalid_multiple_parameters(self):
        params = ImmutableMultiDict([('param1', 1), ('param1', 'a')])
        context = BindingContext(int, 'param1', params, multiple=True)
        self.assertRaises(Exception, self.binder.bind, context)
