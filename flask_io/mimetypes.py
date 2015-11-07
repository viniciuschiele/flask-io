"""
Handling of mimetypes from the HTTP request.
"""


class MimeType(object):
    """
    Represents a mimetype.
    """

    def __init__(self, mimetype):
        """
        Initializes a new instance of MimeType.

        :param str mimetype: The mimetype.
        """
        self.mimetype = mimetype
        self.full_type, self.params = self.__parse_mimetype(mimetype)
        self.main_type, sep, self.sub_type = self.full_type.partition('/')

    def match(self, other):
        """
        Checks if the given MimeType matches to the this MimeType.

        :param MimeType other: The MimeType to compare to.
        :return bool: True if this MimeType matches the given MediaType.
        """
        if self.sub_type != '*' and other.sub_type != '*' and other.sub_type != self.sub_type:
            return False

        if self.main_type != '*' and other.main_type != '*' and other.main_type != self.main_type:
            return False

        return True

    def __parse_mimetype(self, mimetype):
        """
        Extracts the full type and parameters from the given MimeType.
        :param str mimetype: The mimetype to be parsed.
        :return: Returns a tuple with full type and parameters.
        """
        plist = mimetype.split(';')

        full_type = plist.pop(0).lower().strip()
        params = {}

        for p in plist:
            kv = p.split('=')
            if len(kv) != 2:
                continue
            v = kv[1].strip()
            if v:
                params[kv[0].strip()] = v

        return full_type, params
