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


from flask import request
from .binder import Binder

def bind(params):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs.update(Binder.bind(params))
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ValueProvider(object):
    def __init__(self, type_, name=None, default=None, required=False, multiple=False):
        self.type = type_
        self.name = name
        self.default = default
        self.required = required
        self.multiple = multiple

    def get_values(self):
        pass


class FromQuery(ValueProvider):
    def get_values(self):
        return request.args
