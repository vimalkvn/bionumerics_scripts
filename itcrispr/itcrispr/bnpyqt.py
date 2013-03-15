"""Fix for working with multiple PyQt installs.

1. Use local (C:\Python26) PyQt if available
2. If not, use the network version mapped to B:
3. If imports fail from both locations, display a message and exit

"""
import os
import sys
import bns  # IGNORE:F0401 @UnresolvedImport
MessageBox = bns.Util.Program.MessageBox

sys_dirs = [r"c:\python25\lib\site-packages",
		r"c:\python26\lib\site-packages",
		r"b:\\site-packages"]
os.environ["PATH"] = ""
for dname in sys.path:
	if dname.lower() in sys_dirs:
		sys.path.remove(dname)

site_dir = r"c:\python26\lib\site-packages"
sys.path.append(site_dir)
qt_dirs = ("c:\\python26\\lib\\site-packages\\pyqt4;"
		"c:\\python26\\lib\\site-packages\\pyqt4\\bin")
os.environ["PATH"] = qt_dirs

try:
	from PyQt4.QtGui import QApplication  # IGNORE:W0611 @UnusedImport
except ImportError:
	os.environ["PATH"] = ""
	sys.path.remove(site_dir)
	site_dir = r"b:\site-packages"
	sys.path.append(site_dir)

	qt_dirs = "b:\\site-packages\\pyqt4;b:\\site-packages\\pyqt4\\bin"
	os.environ["PATH"] = qt_dirs

	try:
		from PyQt4.QtGui import QApplication  # IGNORE:W0611 @UnusedImport
	except ImportError:
		msg = ("Could not import PyQt4.\n\nPlease install the 32-bit version of"
			"PyQt4 for Python 2.6. It can be downloaded from\n\n"
			"http://www.riverbankcomputing.co.uk/software/pyqt/download\n\n"
			"Restart BioNumerics after installation.")
		MessageBox("Could not import PyQt4", msg, "exclamation")
		raise
