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


from flask_binding.binder import BindingContext
from flask_binding.binders import BooleanBinder
from unittest import TestCase
from werkzeug.datastructures import ImmutableMultiDict


class TestBoolean(TestCase):
    def setUp(self):
        self.binder = BooleanBinder()

    def test_valid_value(self):
        context = BindingContext(int, 'param1', {'param1': 'true'})
        self.assertEqual(self.binder.bind(context), True)

        context = BindingContext(int, 'param1', {'param1': 'True'})
        self.assertEqual(self.binder.bind(context), True)

    def test_invalid_value(self):
        context = BindingContext(int, 'param1', {'param1': 'abc'})
        self.assertEqual(self.binder.bind(context), False)

    def test_empty_value(self):
        context = BindingContext(int, 'param1', {'param1': ''})
        self.assertEqual(self.binder.bind(context), False)

    def test_missing_argument(self):
        context = BindingContext(int, 'param1', {'param2': 1})
        self.assertEqual(self.binder.bind(context), None)

    def test_multiple_parameters(self):
        params = ImmutableMultiDict([('param1', 'T'), ('param1', 'True')])
        context = BindingContext(int, 'param1', params, multiple=True)
        self.assertEqual(self.binder.bind(context), [True, True])

    def test_invalid_multiple_parameters(self):
        params = ImmutableMultiDict([('param1', 'true'), ('param1', 'abc')])
        context = BindingContext(int, 'param1', params, multiple=True)
        self.assertEqual(self.binder.bind(context), [True, False])
