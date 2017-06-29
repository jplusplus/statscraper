# encoding: utf-8

from unittest import TestCase
from statscraper import Datatype, NoSuchDatatype


class TestDatatype(TestCase):

    def test_datatype(self):
        dt = Datatype("str")
        self.assertTrue(str(dt) == "str")

    def test_datatype_with_values(self):
        dt = Datatype("region")
        self.assertTrue(len(dt.allowed_values))

    def test_none_existing_datatype(self):
        with self.assertRaises(NoSuchDatatype):
            Datatype("donkey_power")

    def test_allowed_values(self):
        dt = Datatype("region")

        self.assertTrue(u"Växjö kommun" in dt.allowed_values)

        self.assertEqual(str(dt.allowed_values["eu"]), "eu")

    def test_dialect(self):
        dt = Datatype("region")
        val = dt.allowed_values[u"Växjö kommun"]
        self.assertTrue("wikidata" in val.dialects)
        self.assertEqual(u"Q500217", val.dialects["wikidata"].pop())

        self.assertTrue("scb" in val.dialects)
        self.assertEqual(u"0780 Växjö kommun", val.dialects["scb"].pop())
