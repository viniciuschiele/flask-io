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

from collections import OrderedDict
from flask import request
from werkzeug.http import HTTP_STATUS_CODES
from .errors import Error


def collect_trace_data(action, latency_total, latency_func, error, response):
    data = OrderedDict()
    data['func'] = action.func_name
    if error:
        data['error'] = str(error)
    data['latency_total'] = '%.5f' % latency_total.elapsed
    data['latency_func'] = '%.5f' % latency_func.elapsed
    data['request_method'] = request.environ['REQUEST_METHOD']
    data['request_url'] = request.url

    body = request.get_data(as_text=True)
    if body:
        data['request_body'] = body

    if response:
        data['response_status'] = response.status_code
    return data


def convert_validation_errors(errors, params):
    items = []

    for field, error in errors.items():
        location = next((x[2] for x in params if x[0] == field), None)
        convert_validation_error(field, error, location, items)

    return items


def convert_validation_error(field, error, location, items):
    if isinstance(error, dict):
        for f, e in error.items():
            convert_validation_error(f, e, location, items)
    elif isinstance(error, list):
        error = error[0]
        if isinstance(error, str):
            items.append(Error(error, location=location, field=field))
        elif isinstance(error, dict):
            items.append(Error(error.get('message'), error.get('reason'), location, field))


def errors_to_dict(errors):
    if isinstance(errors, str):
        errors = [Error(errors)]
    elif isinstance(errors, list):
        errors = errors
    else:
        errors = [errors]

    errors_data = []

    for error in errors:
        error_data = {'message': error.message}
        if error.code:
            error_data['code'] = error.code
        if error.location:
            error_data['location'] = error.location
        if error.field:
            error_data['field'] = error.field
        errors_data.append(error_data)

    return errors_data


def get_best_match_for_content_type(mimetypes, default=None):
    content_type = request.headers['content-type']

    if not content_type:
        return default

    mimetype_expected = content_type.split(';')[0].lower()
    for mimetype in mimetypes:
        if mimetype_expected == mimetype:
            return mimetype
    return None


def get_func_name(func):
    return func.__module__ + "." + func.__name__


def get_request_params(data, name, multiple):
    if multiple:
        return data.getlist(name)
    return data.get(name)


def http_status_message(code):
    return HTTP_STATUS_CODES.get(code, '')


def marshal(data, schema, envelope=None):
    if data is not None:
        many = isinstance(data, list)
        data = schema.dump(data, many=many).data

    if envelope:
        return {envelope: data}

    return data


def unpack(value):
    data, status, headers = value + (None,) * (3 - len(value))
    return data, status, headers
