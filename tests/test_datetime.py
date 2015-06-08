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


from datetime import datetime
from flask_binding.binder import BindingContext
from flask_binding.binders import DateTimeBinder
from unittest import TestCase
from werkzeug.datastructures import ImmutableMultiDict


class TestDateTime(TestCase):
    def setUp(self):
        self.binder = DateTimeBinder()

    def test_valid_value(self):
        context = BindingContext(datetime, 'param1', {'param1': '2015-06-08T09:47:43'})
        self.assertEqual(self.binder.bind(context), datetime(2015, 6, 8, 9, 47, 43))

    def test_invalid_value(self):
        context = BindingContext(int, 'param1', {'param1': 'a'})
        self.assertRaises(Exception, self.binder.bind, context)

    def test_empty_value(self):
        context = BindingContext(int, 'param1', {'param1': ''})
        self.assertEqual(self.binder.bind(context), None)

    def test_missing_argument(self):
        context = BindingContext(int, 'param1', {'param2': 1})
        self.assertEqual(self.binder.bind(context), None)

    def test_multiple_parameters(self):
        date1 = datetime(2015, 6, 8, 9, 47, 43)
        date2 = datetime(2015, 6, 9, 9, 47, 43)

        params = ImmutableMultiDict([('param1', '2015-06-08T09:47:43'), ('param1', '2015-06-09T09:47:43')])
        context = BindingContext(int, 'param1', params, multiple=True)
        self.assertEqual(self.binder.bind(context), [date1, date2])

    def test_invalid_multiple_parameters(self):
        params = ImmutableMultiDict([('param1', 1), ('param1', 'a')])
        context = BindingContext(int, 'param1', params, multiple=True)
        self.assertRaises(Exception, self.binder.bind, context)
