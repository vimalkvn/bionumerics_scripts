"""Fix for working with multiple PyQt installs.

1. Use local (C:\Python26) PyQt if available
2. If not, use the network version mapped to B:
3. If imports fail from both locations, display a message and exit

"""
import os
import sys
import Tkinter
import tkMessageBox

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
	from PyQt4.QtGui import QApplication
except ImportError:
	os.environ["PATH"] = ""
	sys.path.remove(site_dir)
	site_dir = r"b:\site-packages"
	sys.path.append(site_dir)

	qt_dirs = "b:\\site-packages\\pyqt4;b:\\site-packages\\pyqt4\\bin"
	os.environ["PATH"] = qt_dirs

	try:
		from PyQt4.QtGui import QApplication
	except ImportError:
		root = Tkinter.Tk()
		root.withdraw()
		msg = ("Cannot import PyQt4\n\nPlease make sure\n"
		"1. PyQt4 for Python 2.6 is installed.\n"
		"2. The PyQt4 DLL directories are added to system PATH.")
		tkMessageBox.showinfo("Cannot import PyQt4", msg)
