from flask_io import missing
from flask_io.mediatypes import MediaType
from unittest import TestCase


class TestMediaType(TestCase):
    def test_full_type(self):
        media_type = MediaType('application/json')

        self.assertEqual('application/json', media_type.full_type)
        self.assertEqual('application', media_type.main_type)
        self.assertEqual('json', media_type.sub_type)
        self.assertEqual({}, media_type.params)

    def test_empty_full_type(self):
        media_type = MediaType('')

        self.assertEqual('', media_type.full_type)
        self.assertEqual('', media_type.main_type)
        self.assertEqual('', media_type.sub_type)

    def test_invalid_full_type(self):
        media_type = MediaType('application')

        self.assertEqual('application', media_type.full_type)
        self.assertEqual('application', media_type.main_type)
        self.assertEqual('', media_type.sub_type)

    def test_with_parameters(self):
        media_type = MediaType('application/json ; encoding = utf-8;identity=4')

        self.assertEqual('application/json', media_type.full_type)
        self.assertEqual('application', media_type.main_type)
        self.assertEqual('json', media_type.sub_type)
        self.assertEqual('utf-8', media_type.params['encoding'])
        self.assertEqual('4', media_type.params['identity'])

    def test_empty_parameter(self):
        media_type = MediaType('application/json;=utf-8;identity=')

        self.assertEqual(missing, media_type.params.get('encoding', missing))
        self.assertEqual('', media_type.params['identity'])

    def test_match(self):
        media_type = MediaType('application/json')
        media_type2 = MediaType('application/json;encoding=utf-8')
        self.assertTrue(media_type.match(media_type2))
        self.assertFalse(media_type2.match(media_type))
