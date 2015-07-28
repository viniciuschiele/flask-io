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
from inspect import isclass


def get_best_match_for_content_type(mimetypes):
    content_type = request.headers['content-type']

    mimetype_expected = content_type.split(';')[0].lower()
    for mimetype in mimetypes:
        if mimetype_expected == mimetype:
            return mimetype
    return None


def new_if_isclass(value):
    if isclass(value):
        return value()
    return value


def unpack(value):
    data, status, headers = value + (None,) * (3 - len(value))
    return data, status, headers
