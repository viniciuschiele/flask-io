def parse_mimetype(mimetype):
    plist = mimetype.split(';')

    full_type = plist.pop(0).lower().strip()
    params = {}

    for p in plist:
        kv = p.split('=')
        if len(kv) == 2:
            params[kv[0].strip()] = kv[1].strip()

    return full_type, params


class MimeType(object):
    def __init__(self, mimetype):
        self.mimetype = mimetype
        self.full_type, self.params = parse_mimetype(mimetype)
        self.main_type, sep, self.sub_type = self.full_type.partition('/')

    def match(self, other):
        """Return true if this MediaType matches the given MediaType."""
        for key in self.params.keys():
            if other.params.get(key, None) != self.params.get(key, None):
                return False

        if self.sub_type != '*' and other.sub_type != '*' and other.sub_type != self.sub_type:
            return False

        if self.main_type != '*' and other.main_type != '*' and other.main_type != self.main_type:
            return False

        return True
