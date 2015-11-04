try:
    import simplejson as json
except ImportError:
    import json


def dumps(s, indent=None):
    return json.dumps(s, indent=indent)


def loads(s):
    return json.loads(s)
