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
from tests.common import TestSource


class TestBoolean(TestCase):
    def setUp(self):
        self.binder = BooleanBinder()

    def test_valid_value(self):
        source = TestSource()
        source.add('param1', 'true')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), True)

    def test_invalid_value(self):
        source = TestSource()
        source.add('param1', 'abc')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), False)

    def test_empty_value(self):
        source = TestSource()
        source.add('param1', '')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), None)

    def test_missing_argument(self):
        source = TestSource()
        source.add('param2', '1')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), None)

    def test_multiple_parameters(self):
        source = TestSource(multiple=True)
        source.add('param1', 'T')
        source.add('param1', 'True')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), [True, True])

    def test_invalid_multiple_parameters(self):
        source = TestSource(multiple=True)
        source.add('param1', 'true')
        source.add('param1', 'abc')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), [True, False])
