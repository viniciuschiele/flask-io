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
from datetime import datetime


def get_default_parsers():
    return {
        bool: BooleanParser(),
        int: PrimitiveParser(int),
        float: PrimitiveParser(float),
        str: PrimitiveParser(str),
        datetime: DateTimeParser()
    }


class InputParser(metaclass=ABCMeta):
    @abstractmethod
    def parse(self, value):
        pass


class PrimitiveParser(InputParser):
    def __init__(self, type_):
        self.type = type_

    def parse(self, value):
        return self.type(value)


class BooleanParser(InputParser):
    TRUE_VALUES = ['yes', 'true', 'y', 't', '1']

    def parse(self, value):
        return value.lower() in self.TRUE_VALUES


class DateTimeParser(InputParser):
    def parse(self, value):
        return dateutil.parser.parse(value)
