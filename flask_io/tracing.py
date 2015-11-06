"""
Logging for HTTP requests.
"""

from collections import OrderedDict
from .utils import format_trace_data


class Tracer(object):
    """
    Responsible to collect and emit the tracing samples.
    """

    def __init__(self, io):
        """
        Initializes a new instance of 'Tracer'.

        :param io: A `FlaskIO` instance.
        """
        self.io = io
        self.filters = []
        self.enabled = False
        self.inspector = lambda data: None
        self.emitter = self.__default_emit_trace

    def add_filter(self, methods=None, endpoints=None):
        """
        Adds a filter.

        :param methods: The HTTP methods to be filtered.
        :param endpoints: The endpoints to be filtered.
        :return Filter: The filter added.
        """
        if not methods and not endpoints:
            raise ValueError('Filter cannot be added with no criteria.')

        filter = TraceFilter(methods, endpoints)
        self.filters.append(filter)
        return filter

    def match(self, rule):
        """
        Checks if the given rule matches with any filter added.

        :param rule: The Flask rule to be matched.
        :return: True if there is a filter that matches.
        """
        if len(self.filters) == 0:
            return True

        for filter in self.filters:
            if filter.match(rule):
                return True
        return False

    def trace(self, request, response, error, latency):
        """
        Collects the data from the given parameters and emit it.

        :param request: The Flask request.
        :param response: The Flask response.
        :param error: The error occurred if any.
        :param latency: The time elapsed to process the request.
        """

        data = self.__collect_trace_data(request, response, error, latency)

        self.inspector(data)
        self.emitter(data)

    def __collect_trace_data(self, request, response, error, latency):
        """
        Collects the tracing data from the given parameters.
        :param request: The Flask request.
        :param response: The flask response.
        :param error: The error occurred if any.
        :param latency: The time elapsed to process the request.
        :return: The tracing data.
        """

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
        """
        Writes the given tracing data to Python Logging.

        :param data: The tracing data to be written.
        """
        message = format_trace_data(data)
        self.io.logger.info(message)


class TraceFilter(object):
    """
    A tracing filter.
    """

    def __init__(self, methods, endpoints):
        """
        Initializes a new instance 'TraceFilter'.

        :param methods: HTTP methods to be filtered.
        :param endpoints: Endpoint names to be filtered.
        """

        self.methods = methods
        self.endpoints = endpoints

    def match(self, rule):
        """
        Checks if the given rule matches with the filter.

        :param rule: The Flask rule to be matched.
        :return: True if the filter matches.
        """
        if self.methods:
            for method in self.methods:
                if method in rule.methods:
                    return True

        if self.endpoints:
            for endpoint in self.endpoints:
                if endpoint == rule.endpoint:
                    return True

        return False
