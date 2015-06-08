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


class ParamBinder(object):
    def bind(self, context):
        pass


class BaseBinder(ParamBinder):
    def bind(self, context):
        if context.multiple:
            return self._bind_multiple(context)

        return self._bind_single(context)

    def _bind_single(self, context):
        value = context.values.get(context.name)

        if value is None or value == '':
            return None

        return self._parse(context, value)

    def _bind_multiple(self, context):
        values = context.values.getlist(context.name)

        if len(values) == 0:
            return None

        ret = []
        for value in values:
            if value is None or value == '':
                continue
            ret.append(self._parse(context, value))
        return ret

    def _parse(self, context, value):
        raise NotImplementedError()


class PrimitiveBinder(BaseBinder):
    def _parse(self, context, value):
        if isinstance(value, context.type):
            return value
        return context.type(value)


class BooleanBinder(BaseBinder):
    TRUE_VALUES = ['yes', 'true', 'y', 't', '1']

    def _parse(self, context, value):
        if isinstance(value, bool):
            return value

        return value.lower() in self.TRUE_VALUES


class DateTimeBinder(BaseBinder):
    def _parse(self, context, value):
        return dateutil.parser.parse(value)


class DictionaryBinder(BaseBinder):
    def _parse(self, context, value):
        if isinstance(value, dict):
            return value
        raise TypeError('value is not a dictionary')
