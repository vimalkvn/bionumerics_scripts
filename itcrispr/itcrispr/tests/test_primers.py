"""Load primers from a directory"""
import os
import sys
import unittest

SCRIPT_PATH = r"C:\Users\vimal\Workspace\itcrispr"
sys.path.append(SCRIPT_PATH)
from itcrispr import primers

DATADIR = os.path.join(SCRIPT_PATH, "itcrispr", "tests", "data")
sys.stderr = open(os.path.join(DATADIR, "test_primers.txt"), "w")


class TestPrimers(unittest.TestCase):

	def testDetectNewLines(self):
		"""New lines in primer sequences should be detected"""
		fname = os.path.join(DATADIR, "primer-newline.txt")
		primer, data = primers.readPrimer(fname)
		self.assertTrue(len(primer))
		self.assertTrue(len(data))

	def testDetectNoFiles(self):
		"""If there are no primer files, handle it"""
		primer_path = os.path.join(DATADIR, "blank")
		if not os.path.exists(primer_path):
			os.mkdir(primer_path)
		result = primers.getList(primer_path)
		self.assertEqual(len(result), 0)
		os.rmdir(primer_path)

	def testDetectDuplicates(self):
		"""Different names, same sequence"""
		primer_path = os.path.join(DATADIR, "dups")
		primer_list, messages = primers.getPrimers(primer_path)
		self.assertTrue(isinstance(primer_list, dict))
		self.assertTrue(len(messages) > 0)

	def testGoodPrimers(self):
		"""If everything is ok, read primers into dictionary"""
		primer_path = os.path.join(DATADIR, "primers")
		primer_list, messages = primers.getPrimers(primer_path)
		self.assertTrue(isinstance(primer_list, dict))
		self.assertTrue(len(primer_list) > 0)
		self.assertTrue(len(messages) == 0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestPrimers)
unittest.TextTestRunner(stream=sys.stderr, verbosity=3).run(suite)

sys.stderr.flush()
