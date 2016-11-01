"""
Handling of mime types, as found in HTTP Content-Type and Accept headers.
"""


class MimeType(object):
    """
    Represents a mimetype.
    """

    def __init__(self, main_type, sub_type, params=None):
        """
        Initializes a new instance of MimeType.
        :param str main_type: The first part of the mimetype before the slash.
        :param str sub_type: The second part of the mimetype after the slash.
        :param dict params: The parameters of the mimetype.
        """
        self.main_type = main_type
        self.sub_type = sub_type
        self.params = params

    def __eq__(self, other):
        """
        Compares the current MimeType against the given MimeType.
        :param MimeType other: The MimeType to be compared.
        :return: True if both MimeType are equals.
        """
        if other is None:
            return False

        return self.main_type == other.main_type and \
               self.sub_type == other.sub_type and \
               self.params == other.params

    def __str__(self):
        """
        Returns the string representation.
        :return: A string.
        """
        ret = self.main_type + '/' + self.sub_type
        for key, val in self.params.items():
            ret += '; ' + key + '=' + val
        return ret

    @classmethod
    def parse(cls, mimetype):
        """
        Extracts the full type and parameters from the given MimeType.
        :param str mimetype: The mimetype to be parsed.
        :return: Returns a tuple with full type and parameters.
        """
        plist = mimetype.split(';')

        main_type, _, sub_type = plist.pop(0).lower().strip().partition('/')
        params = {}

        for p in plist:
            kv = p.split('=')
            if len(kv) != 2:
                continue
            v = kv[1].strip()
            if v:
                params[kv[0].strip()] = v

        return MimeType(main_type, sub_type, params)

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

    def replace(self, main_type=None, sub_type=None, params=None):
        """
        Return a new MimeType with new values for the specified fields.
        :param str main_type: The new main type.
        :param str sub_type: The new sub type.
        :param dict params: The new parameters.
        :return: A new instance of MimeType
        """
        if main_type is None:
            main_type = self.main_type

        if sub_type is None:
            sub_type = self.sub_type

        if params is None:
            params = self.params

        return MimeType(main_type, sub_type, params)
