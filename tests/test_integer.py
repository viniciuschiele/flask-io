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
from flask_binding.binders import PrimitiveBinder
from unittest import TestCase
from tests.common import TestSource


class TestInteger(TestCase):
    def setUp(self):
        self.binder = PrimitiveBinder(int)

    def test_valid_value(self):
        source = TestSource()
        source.add('param1', '10')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), 10)

    def test_invalid_value(self):
        source = TestSource()
        source.add('param1', 'a')
        context = BindingContext('param1', source)
        self.assertRaises(Exception, self.binder.bind, context)

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
        source.add('param1', '1')
        source.add('param1', '2')
        context = BindingContext('param1', source)
        self.assertEqual(self.binder.bind(context), [1, 2])

    def test_invalid_multiple_parameters(self):
        source = TestSource(multiple=True)
        source.add('param1', '1')
        source.add('param1', 'a')
        context = BindingContext('param1', source)
        self.assertRaises(Exception, self.binder.bind, context)
