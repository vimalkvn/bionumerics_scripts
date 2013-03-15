"""BN entry selection and contig deletion tests"""
import os
import sys
import unittest
import bns  # IGNORE:F0401 @UnresolvedImport

SCRIPT_PATH = r"C:\Users\vimal\Workspace\itcrispr"
sys.path.append(SCRIPT_PATH)
from itcrispr import bn

DATADIR = os.path.join(SCRIPT_PATH, "tests", "data")
sys.stderr = open(os.path.join(DATADIR, "test_checklist.txt"), "w")


class TestCheckList(unittest.TestCase):

	def testOnlySelection(self):
		"""Only work on selected entries.

		Note: select an entry in the main window

		"""
		result = bn.getChecklist(["CRISPR1", "CRISPR2"])
		self.assertEqual(len(result), 1)

	def testTwoExper(self):
		"""Two experiments defined for an entry

		select an entry with 2 experiments defined - CRISPR1, CRISPR2

		"""
		result = bn.getChecklist(["CRISPR1", "CRISPR2"])
		self.assertTrue(len(result.values()[0]) == 2)

	def testOneExper(self):
		"""One experiment defined for an entry

		select an entry with 1 experiment defined. In this case there is no
		experiment for CRISPR1

		"""
		result = bn.getChecklist(["CRISPR1", "adk"])
		self.assertTrue(len(result.values()[0]) == 1)

	def testDeleteContigs(self):
		"""Test contig deletion.

		Use an entry with CRISPR1 experiment. Assembly generates 2 contigs
		Delete contig should remove all contigs.

		"""
		asm = bns.Sequences.Assembly()
		asm.OpenWindow("P548104-0", "CRISPR1")
		asm.AlignAll()
		self.assertEqual(len(asm.Contigs), 2)
		bn.deleteContigs(asm)
		self.assertEqual(len(asm.Contigs), 0)
		asm.Close()

suite = unittest.TestSuite()
suite.addTest(TestCheckList("testOneExper"))
#suite = unittest.TestLoader().loadTestsFromTestCase(TestCheckList)
unittest.TextTestRunner(stream=sys.stderr, verbosity=3).run(suite)

sys.stderr.flush()
