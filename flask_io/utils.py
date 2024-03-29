import sys
from collections.abc import Mapping, Sequence

from flask import request
from time import perf_counter
from marshmallow.exceptions import SCHEMA
from werkzeug.http import HTTP_STATUS_CODES

from .errors import Error


def _raise_typeerror(error):
    raise TypeError('Invalid error object of type {}'.format(type(error)))


def errors_to_dict(errors):
    errors_data = []

    if isinstance(errors, str):
        errors_data = [Error(errors).as_dict()]

    elif hasattr(errors, 'as_dict'):
        errors_data = [errors.as_dict()]

    elif isinstance(errors, Sequence) and isinstance(errors[0], Mapping):
        errors_data = errors

    elif isinstance(errors, Sequence):
        errors_data = [error.as_dict()
                       if hasattr(error, 'as_dict')
                       else _raise_typeerror(error)
                       for error in errors]
    else:
        _raise_typeerror(errors)

    return dict(errors=errors_data)


def format_trace_data(data):
    request_method = data.pop('request_method', None)
    request_url = data.pop('request_url', None)
    latency = data.pop('latency', None)
    request_headers = data.pop('request_headers', None)
    request_body = data.pop('request_body', None)
    response_status = data.pop('response_status', None)
    error = data.pop('error', None)

    message = ''

    if request_method:
        message += request_method + ' '

    if request_url:
        message += request_url + ' '

    if response_status:
        message += str(response_status) + ' '

    if latency:
        message += '%.5f' % latency

    message += '\r\n'

    for key, value in data.items():
        message += key + ': ' + str(value) + '\r\n'

    if request_headers:
        for key, value in request_headers.items():
            message += key + ': ' + str(value) + '\r\n'

    if error:
        message += '\r\n' + error
    elif request_body:
        message += '\r\n' + request_body

    return message


def get_fields_from_request(schema=None):
    fields = request.args.get('fields')
    if not fields:
        return ()

    field_names = fields.split(',')

    if schema:
        declared_fields = schema._declared_fields
        field_names = [field_name for field_name in field_names if field_name in declared_fields]

    return tuple(field_names)


def http_status_message(code):
    return HTTP_STATUS_CODES.get(code, '')


def marshal(data, schema, envelope=None):
    if data is not None:
        many = isinstance(data, Sequence)
        data = schema.dump(data, many=many)

    if envelope:
        return {envelope: data}

    return data


def reraise():
    _, exc_value, tb = sys.exc_info()
    if exc_value.__traceback__ is not tb:
        raise exc_value.with_traceback(tb)
    raise exc_value


def unpack(value):
    data, status, headers = value + (None,) * (3 - len(value))
    return data, status, headers


def validation_error_to_errors(validation_error):
    errors = []

    if isinstance(validation_error.messages, Sequence):
        field_names = validation_error.field_names or [SCHEMA]

        for field in field_names:
            validation_error_to_error(field, validation_error.messages, validation_error.kwargs.get('location'), errors)

    else:
        for field, error in validation_error.messages.items():
            validation_error_to_error(field, error, validation_error.kwargs.get('location'), errors)

    return errors


def validation_error_to_error(field, error, location, errors):
    if isinstance(error, dict):
        for f, e in error.items():
            validation_error_to_error(f, e, location, errors)
    elif isinstance(error, Sequence):
        error = error[0]
        if isinstance(error, str):
            errors.append(Error(error, location=location, field=field))
        elif isinstance(error, dict):
            errors.append(Error(error.get('message'), error.get('code'), location, field))


class Stopwatch(object):
    def __init__(self):
        self.elapsed = 0.0
        self._start = None

    @staticmethod
    def start_new():
        sw = Stopwatch()
        sw.start()
        return sw

    def start(self):
        if not self._start:
            self._start = perf_counter()

    def stop(self):
        if self._start:
            end = perf_counter()
            self.elapsed += (end - self._start)
            self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
