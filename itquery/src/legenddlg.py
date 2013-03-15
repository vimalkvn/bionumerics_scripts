import sys
from PyQt4.QtGui import QDialog, QApplication
from PyQt4.QtCore import SIGNAL
from ui_legenddlg import Ui_LegendDlg

class legendDialog(QDialog, Ui_LegendDlg):
	"""A simple dialog displaying the color legends used in itquery."""
	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)
		self.connect(self.close_button, SIGNAL("clicked()"), self.close)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	dlg = legendDialog()
	dlg.show()
	sys.exit(app.exec_())
