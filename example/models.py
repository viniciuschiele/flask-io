class User(object):
    def __init__(self, **kwargs):
        self.username = kwargs.get('username', None)
        self.first_name = kwargs.get('first_name', None)
        self.last_name = kwargs.get('last_name', None)
        self.email = kwargs.get('email', None)
        self.enabled = kwargs.get('enabled', None)
        self.created_at = kwargs.get('created_at', None)
