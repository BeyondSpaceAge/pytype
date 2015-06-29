"""Tests for import."""

from pytype import utils
from pytype.tests import test_inference


class ImportTest(test_inference.InferenceTest):
  """Tests for import."""

  def testBasicImport(self):
    self.assert_ok("""\
      import sys
      """)

  def testPathImport(self):
    self.assert_ok("""\
      import path.to.some.module
      """)

  def testFromImport(self):
    self.assert_ok("""\
      from sys import exit
      from path.to.module import bar, baz
      """)

  def testRelativeImport(self):
    self.assert_ok("""\
      from .. import module
      """)

  def testImportAll(self):
    self.assert_ok("""\
      from module import *
      from path.to.module import *
      """)

  def testAssignMember(self):
    self.assert_ok("""\
      import sys
      sys.path = []
      """)

  def testReturnModule(self):
    with self.Infer("""
        import sys

        def f():
          return sys
        f()
    """, deep=False, solve_unknowns=False, extract_locals=False) as ty:
      self.assertOnlyHasReturnType(ty.Lookup("f"), self.module)

  def testMatchModule(self):
    with self.Infer("""
      import sys
      def f():
        if getattr(sys, "foobar"):
          return {sys: sys}.keys()[0]
        else:
          return sys
      f()
    """, deep=False, solve_unknowns=False, extract_locals=False) as ty:
      self.assertOnlyHasReturnType(ty.Lookup("f"), self.module)

  def testSys(self):
    with self.Infer("""
      import sys
      def f():
        return sys.path
      f()
    """, deep=False, solve_unknowns=False, extract_locals=False) as ty:
      self.assertOnlyHasReturnType(ty.Lookup("f"), self.str_list)

  def testFromSysImport(self):
    with self.Infer("""
      from sys import path
      def f():
        return path
      f()
    """, deep=False, solve_unknowns=False, extract_locals=False) as ty:
      self.assertOnlyHasReturnType(ty.Lookup("f"), self.str_list)

  def testImportPy(self):
    with utils.Tempdir() as d:
      d.create_file("other_file.py", """
        def f():
      """)
      d.create_file("main.py", """
        from other_file import f
      """)
      ty = self.InferFromFile(filename=d["main.py"], pythonpath=[d.path])
      # TODO(kramm): Do more testing here once pludemann@ has implemented logic
      #              for actually using pythonpath. Also below.
      self.assertTrue(ty.Lookup("f"))

  def testImportPytd(self):
    with utils.Tempdir() as d:
      d.create_file("other_file.pytd", """
        def f() -> int
      """)
      d.create_file("main.py", """
        from other_file import f
      """)
      ty = self.InferFromFile(filename=d["main.py"], pythonpath=[d.path])
      self.assertTrue(ty.Lookup("f"))

if __name__ == "__main__":
  test_inference.main()
