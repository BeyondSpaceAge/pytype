"""Tests for pytype.pytd.parse.builtins."""

from pytype.pyi import parser
from pytype.pytd import builtin_stubs
from pytype.pytd import pytd
from pytype.pytd import pytd_utils
from pytype.pytd import visitors
from pytype.tests import test_base

import unittest


class UtilsTest(test_base.UnitTest):

  @classmethod
  def setUpClass(cls):
    super(UtilsTest, cls).setUpClass()
    cls.builtins = pytd_utils.Concat(*builtin_stubs.GetBuiltinsAndTyping(
        parser.PyiOptions(python_version=cls.python_version)))

  def test_get_builtins_pytd(self):
    self.assertIsNotNone(self.builtins)
    # Will throw an error for unresolved identifiers:
    self.builtins.Visit(visitors.VerifyLookup())

  def test_has_mutable_parameters(self):
    append = self.builtins.Lookup("builtins.list").Lookup("append")
    self.assertIsNotNone(append.signatures[0].params[0].mutated_type)

  def test_has_correct_self(self):
    update = self.builtins.Lookup("builtins.dict").Lookup("update")
    t = update.signatures[0].params[0].type
    self.assertIsInstance(t, pytd.GenericType)
    self.assertEqual(t.base_type, pytd.ClassType("builtins.dict"))

  def test_has_object_superclass(self):
    cls = self.builtins.Lookup("builtins.memoryview")
    self.assertEqual(cls.bases, (pytd.ClassType("builtins.object"),))
    cls = self.builtins.Lookup("builtins.object")
    self.assertEqual(cls.bases, ())


if __name__ == "__main__":
  unittest.main()
