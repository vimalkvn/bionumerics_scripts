"""A simple dialog application to set the field of selected entries in 
Bionumerics 6

"""

import sys
import bns

moduledir = [r'C:\Python26\Lib\site-packages', r'G:\Python\Bionumerics_scripts\src']
for moddir in moduledir:
	if moddir not in sys.path:
		sys.path.append(moddir)

import dbf
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication, QDialog, QMessageBox
import ui_setfielddlg

class Dlg(QDialog, ui_setfielddlg.Ui_Dialog):
	
	def __init__(self, fieldnames, parent=None):
		super(Dlg, self).__init__(parent)
		self.setupUi(self)
		
		self.connect(self.close_button, SIGNAL('clicked()'), self.accept)
		self.connect(self.apply_button, SIGNAL('clicked()'), self.setfield)
		self.connect(self.deselect_button, SIGNAL('clicked()'), self.deselect)
		
		if fieldnames:
			self.field_combo_box.addItems(fieldnames)
		else:
			QMessageBox.critical(None, 'Error', 'Could not get fieldnames')
			return
		
	def deselect(self):
		'''Deselect all entries if selected'''
		
		if len(bns.Database.Db.Selection):
			bns.Database.Db.Selection.Clear()
		else:
			return
	
	def setfield(self):
		'''Sets the field value of selected entries'''
		
		field = unicode(self.field_combo_box.currentText())
		value = unicode(self.value_line_edit.text())
		
		selected = dbf.get_selected()
		
		if selected:
			for item in selected:
				key = item.Key
				try:
					bns.Database.EntryField(key, field).Content = value
				except Exception, e:
					QMessageBox.critical(None, 'Error', str(sys.exc_info()))
			
			bns.Database.Db.Fields.Save()
		else:
			QMessageBox.information(None, 'No entries selected', 
								'Please select entries before running script')
		
if __name__ == '__main__':
	
	sys.__dict__['argv'] = ['argv']	
	app = QApplication(sys.argv)
	fields = dbf.get_field_names()	
	dialog = Dlg(fields)
	dialog.show()
	__bnscontext__.Stop(app.exec_())
