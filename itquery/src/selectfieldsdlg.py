import sys
from PyQt4.QtGui import QApplication, QDialog, QListWidgetItem
from PyQt4.QtCore import SIGNAL, QString, Qt

from ui_selectfieldsdlg import Ui_selectFieldsDialog

class selectFieldsDialog(QDialog, Ui_selectFieldsDialog):

	def __init__(self, items=None, parent=None):
		QDialog.__init__(self, parent)
		self.setupUi(self)
		self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
		self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)
		if items is not None:
			for item in sorted(items):
				fieldname = QListWidgetItem(QString(item))
				fieldname.setCheckState(Qt.Unchecked)
				self.fieldListWidget.addItem(fieldname)
				
	def getSelected(self):
		selected = []
		for i in range(self.fieldListWidget.count()):
			item = self.fieldListWidget.item(i)
			if item.checkState() == Qt.Checked:
				selected.append(unicode(item.text()))
		return selected
		
	def setSelected(self, items=None):
		if items is not None:
			for item in items:
				found = self.fieldListWidget.findItems(item, Qt.MatchExactly)
				if len(found):
					found[0].setCheckState(Qt.Checked)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	list_items = ["Strain", "Pathogen Grouping", "Host Type", "City",
		"Disease", "Host", "Year of Isolation", "Serotype", "ST",
		"EcoR_Cluster", "Country", "Continent", "Lab Source", "ST Complex",
		"Group", "Serological Group", "OMP", "Simple Disease", "Simple Patho",
		"Simple Serology", "ShigEHEC", "MSTreeGroup", "StructureA",
		"StructureB1", "StructureB2", "StructureD", "RandomOrder", "Group2",
		"Group3", "Group50%", "group4", "group5", "SimplePathOrNonpath",
		"WasineeCuts", "TranslationFrames", "Lee Insertion Site", "invert",
		"eaeAndescCGrouping", "lifA", "PCR espF-lifA", "intimin type",
		"IMT_Nummer", "OI-122", "espF-lifA", "astA_virulence", "HPI_virulence",
		"iucD_virulence", "iss_virulence", "ColV_virulence", "vat_virulence",
		"tsh_virulence", "papC_virulence", "stx type", "TempGarbage",
		"bgl/Z group", "bgc group", "bgl phenotype", "LEE presence",
		"bgl-Z", "bgc", "bgl-yieH", "test_bgc", "Phenotype", "test-bgl-Z",
		"test-bgl-yieH", "test_bgl-Z_groups", "MLST ST", "MLST CC", "strainid",
		"other_designation", "species", "year_of_isolation", "logbook_date",
		"city_of_isolation", "country_of_isolation", "continent_of_isolation",
		"sender", "senders_continent", "sex_of_patient", "age_of_patient",
		"diagnosis", "lethal", "site_of_isolation", "group_id", "comment",
		"senders_country", "source", "source_details", "Experiment", "Sample",
		"Repeat", "Multiplex", "Layer", "ItemTracker ID"]
	dlg = selectFieldsDialog(list_items)
	dlg.show()
	app.exec_()

