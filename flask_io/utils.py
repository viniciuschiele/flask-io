from flask import request
from time import perf_counter
from marshmallow.marshalling import SCHEMA
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


def get_fields_from_request():
    fields = request.args.get('fields')
    if fields:
        return fields.split(',')
    return ()


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

    if isinstance(validation_error.messages, list):
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
    elif isinstance(error, list):
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
