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

from abc import ABCMeta
from abc import abstractmethod


class ModelBinder(metaclass=ABCMeta):
    @abstractmethod
    def bind(self, context):
        pass


class BaseModelBinder(ModelBinder):
    def bind(self, context):
        if context.source.multiple:
            return self._bind_multiple(context)

        return self._bind_single(context)

    def _bind_single(self, context):
        value = context.source.get_value(context.name)

        if value is None or value == '':
            return None

        return self._parse(value)

    def _bind_multiple(self, context):
        values = context.source.get_values(context.name)

        if len(values) == 0:
            return None

        ret = []
        for value in values:
            if value is None or value == '':
                continue
            ret.append(self._parse(value))
        return ret

    def _parse(self, value):
        raise NotImplementedError()


class PrimitiveBinder(BaseModelBinder):
    def __init__(self, type_):
        self.type = type_

    def _parse(self, value):
        if isinstance(value, self.type):
            return value
        return self.type(value)


class BooleanBinder(BaseModelBinder):
    TRUE_VALUES = ['yes', 'true', 'y', 't', '1']

    def _parse(self, value):
        if isinstance(value, bool):
            return value

        return value.lower() in self.TRUE_VALUES


class DateTimeBinder(BaseModelBinder):
    def _parse(self, value):
        return dateutil.parser.parse(value)


class DictionaryBinder(BaseModelBinder):
    def _parse(self, value):
        if isinstance(value, dict):
            return value
        raise TypeError('value is not a dictionary')
