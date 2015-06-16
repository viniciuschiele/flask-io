from flask_binding.sources import BindingSource
from werkzeug.datastructures import MultiDict


class TestSource(BindingSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__items = MultiDict()

    def add(self, key, value):
        self.__items.add(key, value)

    def get_value(self, key):
        return self.__items.get(key)

    def get_values(self, key):
        return self.__items.getlist(key)
