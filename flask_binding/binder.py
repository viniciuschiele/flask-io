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

import functools

from datetime import datetime
from inspect import isfunction
from .binders import BooleanBinder
from .binders import DateTimeBinder
from .binders import DictionaryBinder
from .binders import PrimitiveBinder
from .errors import InvalidArgumentError
from .errors import RequiredArgumentError


def bind(params):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.update(Binder.bind(params))
            return func(*args, **kwargs)
        return wrapper
    return decorator


class Binder(object):
    binders = {
        bool: BooleanBinder(),
        dict: DictionaryBinder(),
        int: PrimitiveBinder(int),
        float: PrimitiveBinder(float),
        str: PrimitiveBinder(str),
        datetime: DateTimeBinder()
    }

    @staticmethod
    def bind(params):
        kwargs = {}

        for name, source in params.items():
            context = BindingContext(source.name or name, source)

            try:
                binder = Binder.binders[source.type]
                value = binder.bind(context)
            except Exception as e:
                raise InvalidArgumentError(name, e)

            if value is None:
                if source.required:
                    raise RequiredArgumentError(name, 'Argument %s is missing.' % context.name)
                if source.default:
                    if isfunction(source.default):
                        value = source.default()
                    else:
                        value = source.default

            kwargs[name] = value

        return kwargs


class BindingContext(object):
    def __init__(self, name, source):
        self.name = name
        self.source = source
