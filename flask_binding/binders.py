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

import dateutil.parser


class ModelBinder(object):
    def bind(self, context):
        pass


class PrimitiveBinder(ModelBinder):
    def bind(self, context):
        if not context.multiple:
            value = context.values.get(context.name)

            if value is None:
                return None

            return context.type(value)

        values = context.values.getlist(context.name)

        if len(values) == 0:
            return None

        ret = []
        for value in values:
            ret.append(context.type(value))
        return ret


class BooleanBinder(ModelBinder):
    TRUE_VALUES = ['yes', 'true', 'y', 't', '1']

    def bind(self, context):
        if context.multiple:
            return self.bind_multiple(context)

        return self.bind_single(context)

    def bind_single(self, context):
        value = context.values.get(context.name)

        if value is None:
            return None

        return value.lower() in self.TRUE_VALUES

    def bind_multiple(self, context):
        values = context.values.getlist(context.name)

        if len(values) == 0:
            return None

        ret = []
        for value in values:
            ret.append(value.lower() in self.TRUE_VALUES)
        return ret


class DateTimeBinder(ModelBinder):
    def bind(self, context):
        if context.multiple:
            return self.bind_multiple(context)

        return self.bind_single(context)

    def bind_single(self, context):
        value = context.values.get(context.name)

        if value is None:
            return None

        if value == '':
            raise ValueError('value cannot be empty.')

        return dateutil.parser.parse(value)

    def bind_multiple(self, context):
        values = context.values.getlist(context.name)

        if len(values) == 0:
            return None

        ret = []
        for value in values:
            ret.append(dateutil.parser.parse(value))
        return ret
