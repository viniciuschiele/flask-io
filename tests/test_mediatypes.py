from flask_io import missing
from flask_io.mimetypes import MimeType
from unittest import TestCase


class TestMimeType(TestCase):
    def test_full_type(self):
        mimetype = MimeType.parse('application/json')

        self.assertEqual('application', mimetype.main_type)
        self.assertEqual('json', mimetype.sub_type)
        self.assertEqual({}, mimetype.params)

    def test_empty_full_type(self):
        mimetype = MimeType.parse('')

        self.assertEqual('', mimetype.main_type)
        self.assertEqual('', mimetype.sub_type)

    def test_invalid_full_type(self):
        mimetype = MimeType.parse('application')

        self.assertEqual('application', mimetype.main_type)
        self.assertEqual('', mimetype.sub_type)

    def test_with_parameters(self):
        mimetype = MimeType.parse('application/json ; encoding = utf-8;indent=4')

        self.assertEqual('application', mimetype.main_type)
        self.assertEqual('json', mimetype.sub_type)
        self.assertEqual('utf-8', mimetype.params['encoding'])
        self.assertEqual('4', mimetype.params['indent'])

    def test_empty_parameter(self):
        mimetype = MimeType.parse('application/json;=utf-8;indent=')

        self.assertEqual(missing, mimetype.params.get('encoding', missing))
        self.assertEqual(missing, mimetype.params.get('indent', missing))

    def test_match(self):
        mimetype = MimeType.parse('application/json')
        mimetype2 = MimeType.parse('application/json ;encoding=utf-8')
        self.assertTrue(mimetype.match(mimetype2))
        self.assertTrue(mimetype2.match(mimetype))
