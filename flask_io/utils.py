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
from werkzeug.http import HTTP_STATUS_CODES
from .errors import Error


def errors_to_dict(errors):
    if isinstance(errors, str):
        errors = [Error(errors)]
    elif not isinstance(errors, list):
        errors = [errors]

    errors_data = []

    for error in errors:
        errors_data.append(error.as_dict())

    return dict(errors=errors_data)


def get_best_match_for_content_type(mimetypes, default=None):
    content_type = request.headers['content-type']

    if not content_type:
        return default

    mimetype_expected = content_type.split(';')[0].lower()
    for mimetype in mimetypes:
        if mimetype_expected == mimetype:
            return mimetype
    return None


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


def validation_error_to_errors(validation_error):
    errors = []

    for field, error in validation_error.messages.items():
        validation_error_to_error(field, error, validation_error.kwargs.get('location'), errors)

    return errors


def validation_error_to_error(field, error, location, errors):
    if isinstance(error, dict):
        for f, e in error.items():
            validation_error_to_error(f, e, location, errors)
    elif isinstance(error, list):
        error = error[0]
        if isinstance(error, str):
            errors.append(Error(error, location=location, field=field))
        elif isinstance(error, dict):
            errors.append(Error(error.get('message'), error.get('code'), location, field))
