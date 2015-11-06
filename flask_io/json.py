"""
Implementation helpers for the JSON.
"""

try:
    import simplejson as json
except ImportError:
    import json

dumps = json.dumps
loads = json.loads
