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
from time import perf_counter
from .utils import format_trace_data


class Tracer(object):
    def __init__(self, io):
        self.io = io
        self.filters = []
        self.enabled = False
        self.inspector = lambda data: None
        self.emitter = self.__default_emit_trace

    def add_filter(self, methods=None, endpoints=None):
        if not methods and not endpoints:
            raise ValueError('Filter cannot be added with no criteria.')

        filter = TraceFilter(methods, endpoints)
        self.filters.append(filter)
        return filter

    def match(self, rule):
        if len(self.filters) == 0:
            return True

        for filter in self.filters:
            if filter.match(rule):
                return True
        return False

    def trace(self, request, response, error, latency):
        data = self.__collect_trace_data(request, response, error, latency)

        self.inspector(data)
        self.emitter(data)

    def __collect_trace_data(self, request, response, error, latency):
        data = OrderedDict()
        data['latency'] = latency.elapsed
        data['request_method'] = request.environ['REQUEST_METHOD']
        data['request_url'] = request.url
        data['request_headers'] = request.headers

        body = request.get_data(as_text=True)
        if body:
            data['request_body'] = body

        if response:
            data['response_status'] = response.status_code

        if error:
            data['error'] = str(error)

        return data

    def __default_emit_trace(self, data):
        message = format_trace_data(data)
        self.io.logger.info(message)


class TraceFilter(object):
    def __init__(self, methods, endpoints):
        self.methods = methods
        self.endpoints = endpoints

    def match(self, rule):
        if self.methods:
            for method in self.methods:
                if method in rule.methods:
                    return True

        if self.endpoints:
            for endpoint in self.endpoints:
                if endpoint == rule.endpoint:
                    return True

        return False


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
