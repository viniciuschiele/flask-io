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

from datetime import datetime


def register_default_parsers(io):
    io.register_parser(bool, parse_bool)
    io.register_parser(int, parse_primitive)
    io.register_parser(float, parse_primitive)
    io.register_parser(str, parse_primitive)
    io.register_parser(datetime, parse_datetime)


def parse_bool(type_, value):
    if value is None:
        raise TypeError('value cannot be None.')

    value = value.lower()

    if value in ['yes', 'true', 'y', 't', '1']:
        return True

    if value in ['no', 'false', 'n', 'f', '0']:
        return False

    raise ValueError('value cannot be parsed into bool: ' + value)


def parse_datetime(type_, value):
    if value is None:
        raise TypeError('value cannot be NoneType.')

    if not value.strip():
        raise ValueError('value cannot be empty.')

    return dateutil.parser.parse(value)


def parse_primitive(type_, value):
    return type_(value)
