import json

from abc import ABCMeta
from abc import abstractmethod
from flask import request


class BindingSource(metaclass=ABCMeta):
    def __init__(self, type_=None, name=None, default=None, required=False, multiple=False):
        self.type = type_ or str
        self.name = name
        self.default = default
        self.required = required
        self.multiple = multiple

    @abstractmethod
    def get_value(self, key):
        pass

    @abstractmethod
    def get_values(self, key):
        pass


class FromBody(BindingSource):
    def get_value(self, key):
        data = request.get_data(as_text=True)

        if request.content_type == 'application/json':
            if data != '':
                data = json.loads(data)

        return data

    def get_values(self, key):
        raise NotImplementedError('get_values is not supported.')


class FromCookie(BindingSource):
    def get_value(self, key):
        return request.cookies.get(key)

    def get_values(self, key):
        return request.cookies.getlist(key)


class FromForm(BindingSource):
    def get_value(self, key):
        return request.form.get(key)

    def get_values(self, key):
        return request.form.getlist(key)


class FromHeader(BindingSource):
    def get_value(self, key):
        return request.headers.get(key)

    def get_values(self, key):
        return request.headers.getlist(key)


class FromQuery(BindingSource):
    def get_value(self, key):
        return request.args.get(key)

    def get_values(self, key):
        return request.args.getlist(key)
