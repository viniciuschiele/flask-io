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


from .binders import PrimitiveBinder
from .errors import InvalidArgumentError
from .errors import RequiredArgumentError


class Binder(object):
    binders = {
        int: PrimitiveBinder(),
        str: PrimitiveBinder()
    }

    @staticmethod
    def bind(params):
        kwargs = {}

        for name, param in params.items():
            context = BindingContext()
            context.name = param.name or name
            context.type = param.type
            context.multiple = param.multiple
            context.values = param.get_values()

            binder = Binder.binders[param.type]

            try:
                value = binder.bind(context)
            except Exception as e:
                raise InvalidArgumentError(name, e)

            if value is None:
                if param.required:
                    raise RequiredArgumentError(name)
                value = param.default

            kwargs[name] = value

        return kwargs


class BindingContext(object):
    def __init__(self, type_=None, name=None, values=None, multiple=False):
        self.type = type_
        self.name = name
        self.values = values
        self.multiple = multiple
