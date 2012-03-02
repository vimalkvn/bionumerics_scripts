"""Using the unittest module"""
import bns
import os
import sys
import unittest

#can't access the print window so we write to a text file
#saved under Bionumerics HOME\database
sys.stderr = open(os.path.join(bns.Database.Db.Info.Path, 'unittest.txt'), 'w')

class TestFunc(unittest.TestCase):
	
	def testAmazingFunction(self):
		"""This test will always work!"""
		pass
		
suite = unittest.TestLoader().loadTestsFromTestCase(TestFunc)
unittest.TextTestRunner(stream=sys.stderr, verbosity=3).run(suite)
