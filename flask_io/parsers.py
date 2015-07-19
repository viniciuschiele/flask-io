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


def register_default_parsers(io):
    io.register_parser(BooleanParser())
    io.register_parser(PrimitiveParser(int))
    io.register_parser(PrimitiveParser(float))
    io.register_parser(PrimitiveParser(str))
    io.register_parser(DateTimeParser())


class Parser(metaclass=ABCMeta):
    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def parse(self, value):
        pass


class PrimitiveParser(Parser):
    def __init__(self, type_):
        self.__type = type_

    @property
    def type(self):
        return self.__type

    def parse(self, value):
        return self.__type(value)


class BooleanParser(Parser):
    TRUE_VALUES = ['yes', 'true', 'y', 't', '1']

    @property
    def type(self):
        return type(bool)

    def parse(self, value):
        return value.lower() in self.TRUE_VALUES


class DateTimeParser(Parser):
    @property
    def type(self):
        return type(datetime)

    def parse(self, value):
        return dateutil.parser.parse(value)
