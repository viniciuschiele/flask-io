from abc import ABCMeta
from abc import abstractmethod
from flask import request


class InputSource(metaclass=ABCMeta):
    @abstractmethod
    def get_value(self, key, multiple=False):
        pass


class BodySource(InputSource):
    def get_value(self, key, multiple=False):
        return request.get_data(as_text=True)


class CookieSource(InputSource):
    def get_value(self, key, multiple=False):
        if multiple:
            return request.cookies.getlist(key)
        return request.cookies.get(key)


class FormSource(InputSource):
    def get_value(self, key, multiple=False):
        if multiple:
            return request.form.getlist(key)
        return request.form.get(key)


class HeaderSource(InputSource):
    def get_value(self, key, multiple=False):
        if multiple:
            return request.headers.getlist(key)
        return request.headers.get(key)


class QuerySource(InputSource):
    def get_value(self, key, multiple=False):
        if multiple:
            return request.args.getlist(key)
        return request.args.get(key)
