"""ITQuery - Interface to query ItemTracker and Cherry picking database from
 Bionumerics.

"""
import bns
import os
import sys
import time
import logging
import site

# BN doesn't include script dir automatically
SCRIPT_PATH = r"C:\Users\vimal\Workspace\itquery\src"
site.addsitedir(SCRIPT_PATH)

# Load local PyQt if available
import bnpyqt

# for Jana's New_GetTubesForStrainsInBNAndUpdate module
#site.addsitedir(r'E:\Python\TestScriptsItemTracker\TestJana\HistoryChange')

from PyQt4.QtCore import (QSettings, QVariant, QPoint, QSize, QString,
        QTimer, PYQT_VERSION_STR, QT_VERSION_STR, Qt, QRegExp, QFile,
        QFileInfo, QTextStream)
from PyQt4.QtGui import (QApplication, QMainWindow, QMessageBox, QPushButton,
        QIcon, QActionGroup, QLabel, QTreeWidgetItem, QBrush, QColor,
        QTreeWidgetItemIterator, QSortFilterProxyModel, QStandardItemModel,
         QAbstractItemView, QProgressBar, QFileDialog)
from ui_mainwindow import Ui_MainWindow
import selectfieldsdlg
import legenddlg
import lims
#import New_GetTubesForStrainsInBNAndUpdate as lims
import bn
import pgdb

DB = bns.Database

__version__ = "2.0.8"

CHERRY_COLUMNS = ["Key", "Gene", "Orientation", "Username", "Status", "DNA",
				 "DNA Concentraion", "Volume", "Freezer", "Rack", "Shelf",
				  "Plate Rack", "Position"]


class SortFilterProxyModel(QSortFilterProxyModel):
	"""Multiple filter implementation for the Cherry Picking view."""

	def __init__(self, parent=None):
		super(SortFilterProxyModel, self).__init__(parent)
		self.traceStatus = ""

	def setTraceStatus(self, status):
		"""Filter traces based on their status - Repeat, Finished, Picked."""
		self.traceStatus = status
		self.invalidateFilter()

	def filterAcceptsRow(self, sourceRow, sourceParent):
		"""Test each row for user and trace filters. Return True/False and that
		affects the rows displayed.

		"""
		index1 = self.sourceModel().index(sourceRow, 3, sourceParent)
		index2 = self.sourceModel().index(sourceRow, 4, sourceParent)

		user = self.sourceModel().data(index1).toString()
		status = self.sourceModel().data(index2).toString()

		# set wildcard for user
		if user == "All":
			user = "."

		check1 = self.filterRegExp().indexIn(user)
		check2 =  self.checkTraceStatus(status)

		return (check1 >= 0 and check2)

	def checkTraceStatus(self, status):
		"""Filters traces based on current status or displays all of them if
		"All" is selected.

		"""
		if (self.traceStatus == "All") or (status == self.traceStatus):
			return True
		else:
			return False


class Form(QMainWindow, Ui_MainWindow):
	"""IT Query Main Window."""

	def __init__(self, initIds, initErrIds, parent=None):
		"""Setup main window and populate with data(if given)."""
		super(Form, self).__init__(parent)
		self.setupUi(self)
		self.setWindowTitle("IT Query {0}".format(__version__))
		self.selectedIds = initIds
		self.errorIds = initErrIds

		LOG_LEVEL = logging.INFO
		currTime = time.localtime()
		runDate = time.strftime("%Y-%m-%d", currTime)
		self.dbPath = DB.Db.Info.Path
		LOG_FNAME = "{0}\{1}-{2}.{3}".format(self.dbPath, "itquery",
											 runDate, "txt")

		if LOG_LEVEL == logging.INFO:
			LOG_FORMAT = "%(asctime)s\t%(message)s"
		else:
			LOG_FORMAT = ("%(asctime)s - %(levelname)s - %(funcName)s "
						" - %(message)s")

		self.logger = logging.getLogger("itquery")
		self.logger.setLevel(LOG_LEVEL)
		self.handler = logging.FileHandler(LOG_FNAME)
		formatter = logging.Formatter(LOG_FORMAT)
		self.handler.setFormatter(formatter)
		self.logger.addHandler(self.handler)

		for action, slot in ((self.updateButton, self.updateSelection),
							(self.bionumericsButton, self.bnSelectFields),
							(self.itemTrackerButton, self.itSelectFields)):
			action.clicked.connect(slot)

		for action, slot in ((self.actionCollapseAll, self.collapseAll),
							(self.actionExpandAll, self.expandAll),
							(self.actionCollapseItem, self.collapseItem),
							(self.actionCherryPicking, self.cherryPicking),
							(self.actionExpandItem, self.expandItem),
							(self.actionSelectAll, self.selectAll),
							(self.actionSelectDNA, self.selectDNA),
							(self.actionSelectFrozenStock, self.selectFrozenStock),
							(self.actionSelectInvert, self.selectInvert),
							(self.actionSelectNone, self.selectNone),
							(self.actionGetAllSelected, self.getAllSelected),
							(self.actionRefresh, self.refresh),
							(self.actionAbout, self.about),
							(self.actionViewTree, self.viewTree),
							(self.actionClearLog, self.clearLog),
							(self.actionLegend, self.legend),
							(self.actionExportTraceList, self.exportTraceList),
							(self.actionExportDNAList, self.exportDNAList),
							(self.actionClose, self.close)):
			action.triggered.connect(slot)

		self.treeWidget.itemSelectionChanged.connect(self.updateInfo)
		self.viewMenu.addAction(self.logDockWidget.toggleViewAction())
		icon = QIcon(":/text-x-log.png")
		self.logDockWidget.toggleViewAction().setIcon(icon)
		self.actionSelectInBionumerics.toggled.connect(self.selectInBionumerics)

		self.userComboBox.currentIndexChanged.connect(self.userChanged)
		self.statusComboBox.currentIndexChanged.connect(self.statusChanged)

		self.treeActions = QActionGroup(self)
		self.treeActions.addAction(self.actionExpandItem)
		self.treeActions.addAction(self.actionCollapseItem)
		self.treeActions.addAction(self.actionExpandAll)
		self.treeActions.addAction(self.actionCollapseAll)

		self.selectActions = QActionGroup(self)
		self.selectActions.addAction(self.actionSelectAll)
		self.selectActions.addAction(self.actionSelectNone)
		self.selectActions.addAction(self.actionSelectInvert)
		self.selectActions.addAction(self.actionSelectDNA)
		self.selectActions.addAction(self.actionSelectFrozenStock)

		self.exportActions = QActionGroup(self)
		self.exportActions.addAction(self.actionExportDNAList)
		self.exportActions.addAction(self.actionExportTraceList)

		self.statusbar.setSizeGripEnabled(True)
		# user label at the right end of status bar
#		db = lims.DATABASE
		db = "No information"
		dbLabel  = QLabel("Database: <b>{0}</b>".format(db))
		self.statusbar.addPermanentWidget(dbLabel)
		user = os.environ.get("USERNAME") or "Demo user"
		label = QLabel("Logged in as: <b>{0}</b>".format(user))
		self.statusbar.addPermanentWidget(label)

		# restore main window state
		settings = QSettings()
		size = settings.value("MainWindow/Size",
							 QVariant(QSize(600, 500))).toSize()
		self.resize(size)
		position = settings.value("MainWindow/Position",
								 QVariant(QPoint(0, 0))).toPoint()
		self.move(position)
		self.restoreState(settings.value("MainWindow/State").toByteArray())
		splitterState = settings.value("MainWindow/SplitState").toByteArray()
		self.splitter.restoreState(splitterState)

		# selected fields
		self.dbName = bns.ConnectedDb.ConnectDb.GetList()
		regKey = "Bionumerics/{0}/SelFields".format(self.dbName)
		regBnFields = settings.value(regKey).toStringList()
		self.bnSelectedFields = [unicode(item) for item in regBnFields]

		regItFields = settings.value("ItemTracker/SelFields").toStringList()
		self.itSelectedFields = [unicode(item) for item in regItFields]

		# progress bar
		self.progressBar = QProgressBar(self)
		self.progressBar.setMaximumWidth(200)
		self.statusbar.insertPermanentWidget(0, self.progressBar)
		self.progressBar.hide()

		# initialize variables
		self.itemIds = {}
		self.itemNames = {}
		# bnFields - bionumerics information in the info panel
		self.bnFields = {}
		self.strainInfo = {}
		# maintains list of keys that are updated
		self.updatedStrains = []
		self.selectRadioButton.setChecked(True)
		self.itemProperties = {}
		self.tableResults = []
		self.getBnFields()
		self.mkInfo("{0}. Log: {1}".format(time.asctime(), LOG_FNAME))
		self.populatedTree = False
		self.populatedTable = False
		self.populatedCherry = False
		idField = "ItemTracker ID"  # Field with ItemTracker ID

		self.itemIdsAll, errors = bn.getItemIds(idField, DB.Db.Entries)
		if len(errors):
			for key, message in errors.iteritems():
				self.mkError("Key: {0}, {1}".format(key, message))
		self.database = None
		self.updateUi()

		self.proxyModel = SortFilterProxyModel(self)
		self.proxyModel.setDynamicSortFilter(True)
		self.cherryView.setModel(self.proxyModel)
		self.cherryView.setAlternatingRowColors(True)
		self.cherryView.setSortingEnabled(True)
		self.cherryView.verticalHeader().setVisible(False)
		self.cherryView.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.cherryView.horizontalHeader().setStretchLastSection(True)
		#self.populateTree() # testing
		QTimer.singleShot(0, self.populateTree)

	def bnSelectFields(self):
		"""Bionumerics field selection dialog."""
		try:
			fieldNames = bn.getFieldNames()
		except RuntimeError as e:
			self.mkError("Failed to get Bionumerics field names: {0}".format(e))

		dialog = selectfieldsdlg.selectFieldsDialog(fieldNames, self)
		if self.bnSelectedFields is not None:
			dialog.setSelected(self.bnSelectedFields)

		if dialog.exec_():
			self.bnSelectedFields = dialog.getSelected()
			self.updateInfo()

	def addCherryData(self, model, row):
		"""Inserts row into model"""
		model.insertRow(0)
		for position, value in enumerate(row):
			model.setData(model.index(0, position), value)

	def createCherryModel(self, data, parent):
		"""Creates a model for the tableview using data retrieved from the
		cherry picking database.

		"""
		total = len(data)
		self.progressBar.setMaximum(total)
		self.progressBar.show()
		model = QStandardItemModel(0, len(CHERRY_COLUMNS), parent)
		for position, column in enumerate(CHERRY_COLUMNS):
			model.setHeaderData(position, Qt.Horizontal, column)

		# get additional data for each item
		keys = [item[CHERRY_COLUMNS.index("Key")] for item in data]
		itemIds = []
		missing = []
		itemIdsAll = dict((v, k) for k, v in self.itemIdsAll.iteritems())
		for key in keys:
			if key in itemIdsAll:
				itemIds.append(itemIdsAll[key])
			else:
				missing.append(key)

		if len(missing):
			msg = ("Keys exist in cherry picking database but absent "
				"in Bionumerics {0}".format(", ".join(missing)))
			self.mkWarn(msg)

		if not len(itemIds):
			msg = "No entries in cherry picking database"
			self.statusBar().showMessage(msg, 5000)
			self.mkInfo(msg)
			return None
		itemIds = list(set(itemIds))
		(dnaData, noData, errors) = lims.GetNewestDNAForCherryPicking(itemIds)
		if len(noData):
			msg = ", ".join(str(item) for item in noData)
			self.mkWarn("{0}: {1}".format("No DNA's for these strains", msg))

		if len(errors):
			msg = ", ".join(errors)
			self.mkError(msg)

		for count, result in enumerate(data):
			result = list(result)
			key = result[0]
			if key in itemIdsAll:
				self.progressBar.setValue(count)
				#QApplication.processEvents()
				parentID = itemIdsAll[key]

				if parentID in dnaData:
					properties = dnaData[parentID]
					for value in ("ItemName", "DNA concentration", "Volume",
								 "Freezer", "Rack", "Shelf", "PlateRack",
								  "Position"):
						if value in properties:
							result.append(properties[value])
						else:
							result.append("")
			self.addCherryData(model, result)
		return model

	def cherryPicking(self):
		"""Populate the cherry picking table"""
		if self.populatedCherry:
			if not self.stackedWidget.currentIndex() == 2:
				self.stackedWidget.setCurrentIndex(2)
				self.updateUi()
			return
		self.statusbar.showMessage("Getting data from cherry picking database")

		db = DB.Db.Info.Name
		cherryData = pgdb.get_data(db)

		if not len(cherryData):
			msg = "No cherry picking entries for this database"
			self.statusbar.showMessage(msg, 5000)
			self.mkInfo(msg)
			self.stackedWidget.setCurrentIndex(2)
			self.updateUi()
			return

		self.userComboBox.clear()
		self.statusComboBox.clear()
		# filter combo boxes
		for label, combo in (("Username", self.userComboBox),
							("Status", self.statusComboBox)):
			position = CHERRY_COLUMNS.index(label)
			comboItems = set([item[position] for item in cherryData])
			combo.addItem("All")
			combo.addItems(list(comboItems))

		self.proxyModel.traceStatus = self.statusComboBox.currentText()
		self.cherryView.reset()
		self.cherryView.setDisabled(True)
		self.statusbar.showMessage("Getting data from ItemTracker")

		model = self.createCherryModel(cherryData, self)
		if not model:
			self.cherryView.setEnabled(False)
			self.filterGroupBox.setDisabled(True)
		else:
			self.proxyModel.setSourceModel(model)
			self.cherryView.setEnabled(True)
			self.filterGroupBox.setEnabled(True)

		self.cherryView.resizeColumnsToContents()
		self.updateCounts()
		self.stackedWidget.setCurrentIndex(2)  # switch view to table
		self.statusbar.clearMessage()
		self.progressBar.setValue(len(cherryData))
		self.progressBar.hide()
		self.populatedCherry = True
		self.updateUi()

	def statusChanged(self):
		"""Filter cherry picking based on current trace status from combo box."""
		self.proxyModel.setTraceStatus(self.statusComboBox.currentText())
		self.updateCounts()

	def userChanged(self):
		"""Filter cherry picking based on current user from combo box."""
		user = self.userComboBox.currentText()
		if user == "All":
			user = "."
		regExp = QRegExp(user, Qt.CaseInsensitive, QRegExp.RegExp2)
		self.proxyModel.setFilterRegExp(regExp)
		self.updateCounts()

	def updateCounts(self):
		"""Update counts of strains, traces and DNA in cherry picking"""
		strains = []
		traces = self.proxyModel.rowCount()
		dna = []

		for i in range(traces):
			for field, totals in (("Key", strains), ("DNA", dna)):
				index = self.proxyModel.index(i, CHERRY_COLUMNS.index(field))
				data = self.proxyModel.data(index).toString().trimmed()
				if len(data) and data not in totals:
					totals.append(data)

		self.strainsLcdNumber.display(len(strains))
		self.tracesLcdNumber.display(traces)
		self.dnaLcdNumber.display(len(dna))

	def getSaveFile(self, caption=""):
		"""Opens the save file dialog and returns the file name."""
		if not len(caption):
			caption = "Save File As"

		fn = QFileDialog.getSaveFileName(self, caption, self.dbPath,
										 "Text files (*.txt);;All Files (*.*)")
		if fn:
			if QFileInfo(fn).suffix().isEmpty():
				fn += ".txt"
		return fn

	def exportTextFile(self, fh=None, header=None, data=None):
		"""Writes data to the given file. Accepts column names and the data as
		arguments

		"""
		if not fh:
			self.mkError("Could not open file for writing")
			return

		if not data:
			data = []

		if not len(data):
			self.mkWarn("No data to write")
			return

		fname = QFile(fh)
		if fname.open(QFile.WriteOnly | QFile.Text):
			txt = QTextStream(fname)
			if header:
				txt << ", ".join(col for col in header)
			txt << "\n"
			txt << "\n".join(", ".join(item) for item in data)

			msg = "File export complete: {0}".format(str(fname.fileName()))
			self.mkSuccess(msg)

	def exportDNAList(self):
		"""Export list of DNA's displayed in cherry picking."""
		data = []
		keys = []

		columns = CHERRY_COLUMNS[:]
		excludeColumns = ["Gene", "Orientation"]
		exclude = []

		for item in excludeColumns:
			exclude.append(CHERRY_COLUMNS.index(item))
			columns.remove(item)

		keyIndex = CHERRY_COLUMNS.index("Key")
		dnaIndex = CHERRY_COLUMNS.index("DNA")
		for i in range(0, self.proxyModel.rowCount()):
			# continue if key exists in keys
			index = self.proxyModel.index(i, keyIndex)
			key = self.proxyModel.data(index).toString()

			if key in keys:
				continue
			# continue if DNA column is empty
			index = self.proxyModel.index(i, dnaIndex)
			dna = self.proxyModel.data(index).toString()

			if dna.isEmpty():
				continue
			row = []
			for j in range(self.proxyModel.columnCount()):
				if j in exclude:
					continue
				index = self.proxyModel.index(i, j)
				value = self.proxyModel.data(index).toString()

				if not value.isEmpty():
					row.append(str(value))
				else:
					row.append("")
			data.append(row)
			keys.append(key)

		fh = self.getSaveFile("Export DNA List")
		self.exportTextFile(fh, columns, data)

	def exportTraceList(self):
		"""Export list of traces displayed in cherry picking."""
		data = []
		for i in range(0, self.proxyModel.rowCount()):
			row = []
			for j in range(self.proxyModel.columnCount()):
				index = self.proxyModel.index(i, j)
				value = self.proxyModel.data(index).toString()
				if not value.isEmpty():
					row.append(str(value))
				else:
					row.append("")
			data.append(row)

		fh = self.getSaveFile("Export Trace List")
		columns = CHERRY_COLUMNS[:]
		self.exportTextFile(fh, columns, data)

	def clearLog(self):
		"""Clears the log window"""
		self.logBrowser.clear()

	def closeEvent(self, event):
		"""Called on closing the window. Save settings and exit."""
		self.handler.close()
		self.logger.removeHandler(self.handler)

		if self.okToContinue():
			settings = QSettings()
			settings.setValue("MainWindow/Size", QVariant(self.size()))
			settings.setValue("MainWindow/Position", QVariant(self.pos()))
			settings.setValue("MainWindow/State", QVariant(self.saveState()))
			settings.setValue("MainWindow/SplitState",
							 self.splitter.saveState())

			bnSelectedFields = QVariant(self.bnSelectedFields) \
			if self.bnSelectedFields else QVariant()
			regkey = "Bionumerics/{0}/SelFields".format(self.dbName)
			settings.setValue(regkey, bnSelectedFields)

			itSelectedFields = QVariant(self.itSelectedFields) \
			if self.itSelectedFields else QVariant()
			settings.setValue("ItemTracker/SelFields", itSelectedFields)
		else:
			event.ignore()

	def collapseItem(self):
		"""Collapse selected item."""
		try:
			selected = self.treeWidget.selectedItems()[0]
		except IndexError:
			selected = None
			self.statusbar.showMessage("No item selected", 2000)

		if selected:
			self.treeWidget.collapseItem(selected)

	def collapseAll(self):
		"""Collapse all items."""
		self.treeWidget.collapseAll()

	def disableWidgets(self, widgets):
		"""Disable group of widgets. Does not change visibility."""
		for widget in widgets:
			if widget.isEnabled():
				widget.setDisabled(True)

	def enableWidgets(self, widgets):
		"""Enable group of widgets. Set visible if not visible."""
		for widget in widgets:
			if not widget.isEnabled():
				widget.setEnabled(True)
			if not widget.isVisible():
				widget.setVisible(True)

	def expandItem(self):
		"""Expand selected item."""
		try:
			selected = self.treeWidget.selectedItems()[0]
		except IndexError:
			selected = None
			self.statusbar.showMessage("No item selected", 2000)

		if selected:
			self.treeWidget.expandItem(selected)

	def expandAll(self):
		"""Expands all items."""
		self.treeWidget.expandAll()

	def getBnFields(self):
		"""Get bionumerics field information required for the info panel."""
		bnFields = bn.getFieldNames()
		strainFields = ["Strain", "STRAIN"]

		for field in strainFields:
			if (field in bnFields) and (field not in self.bnSelectedFields):
				self.bnSelectedFields.append(field)

		for key in self.selectedIds.values():
			if not self.bnFields.get(key):
				self.bnFields[key] = bn.getSelectedFields(key, bnFields)

	def getParent(self, item):
		"""Returns the top level parent of an item."""
		parentItem = None

		while item.parent():
			parentItem = item.parent()
			item = parentItem
		return parentItem

	def getData(self, items, itemid):
		"""Returns parent and children for data received from GetDictionary."""
		if len(items):
			children = items[itemid].keys()
			yield itemid, children
			items = items[itemid]

			for child in children:
				for res in self.getData(items, child):
					yield res
		return

	def getAllItemIds(self):
		"""Gets all ItemTracker IDs in the current Bionumerics database."""
		itemIds = {}
		field = "ItemTracker ID"
		value = None
		for i in range(len(DB.Db.Entries)):
			value = DB.Db.Entries[i].Field(field).Content
			# bugfix: don't display if ItemTracker ID contains spaces
			value = value.strip()
			if not len(value):
				continue

			key = DB.Db.Entries[i].Key
			key = key.strip()
			if key in itemIds:
				itemIds.pop(key)
				msg = "Duplicate keys in database: {0}. Not processed".format(key)
				self.mkWarn(msg)
				continue

			try:
				value = int(value)
			except (ValueError, TypeError):
				self.mkWarn("Invalid ItemTracker ID {0} for entry "
						"{1} in Bionumerics".format(value, key))

			if isinstance(value, int):
				if value in itemIds.values():
					msg = ("Duplicate ItemTracker ID: {0}. "
						"Keys: {1}, ".format(value, key))
					for k, v in itemIds.items():
						if v == value:
							itemIds.pop(k)
							msg += k
					self.mkWarn(msg)
				else:
					itemIds[key] = value

		return itemIds

	def getAllSelected(self):
		"""Get all selected items by user."""
		if self.populatedTable:
			self.stackedWidget.setCurrentIndex(1)
			self.updateUi()
			return
		msg = "Getting all selected entries from ItemTracker. Please wait..."
		self.statusbar.showMessage(msg)

		if len(self.itemIdsAll):
			try:
				self.tableResults = \
				lims.SelectAllselectedEntries(self.itemIdsAll.keys())
			except:
				raise RuntimeError
		else:
			self.mkInfo("No ItemTracker IDs to process")

		if not len(self.tableResults):
			user = os.environ.get("USERNAME")
			msg = "No selected entries for user {0}".format(user)
			self.statusbar.showMessage(msg, 5000)
			self.mkInfo(msg)
			self.stackedWidget.setCurrentIndex(1)
			self.populatedTable = False
			self.updateUi()
		else:
			QTimer.singleShot(0, self.populateTable)

	def getItemtrackerFields(self):
		"""Returns all ItemTracker fields returned from GetDictionary."""
		fields = []
		alwaysFields = ["ItemID", "ItemName", "Position"]

		for item in self.itemProperties:
			for field in self.itemProperties[item].keys():
				if (field not in fields) and (field not in alwaysFields):
					fields.append(field)
		return fields

	def getWidget(self):
		"""Returns the current active widget."""
		index = self.stackedWidget.currentIndex()
		if index == 0:
			widget = self.treeWidget
		elif index == 1:
			widget = self.selectedWidget
		elif index == 2:
			widget = self.cherryView

		return widget

	def about(self):
		"""About box."""
		import platform
		msg = """\
		<b>IT Query</b> version {0} <p>An interface to query
		ItemTracker from Bionumerics</p>Python {1} - Qt {2} -
		PyQt {3} on {4}\
		""".format(__version__, platform.python_version(),
				QT_VERSION_STR, PYQT_VERSION_STR, platform.system())

		msg += """<br>Icons from the
		<a href="http://www.oxygen-icons.org/">Oxygen project</a>
		</p>"""
		QMessageBox.about(self, "About IT Query", msg)

	def legend(self):
		"""A simple dialog displaying the color legend used in treeview."""
		dialog = legenddlg.legendDialog(self)
		dialog.exec_()

	def itSelectFields(self):
		"""ItemTracker field selection dialog."""
		fieldNames = self.getItemtrackerFields()
		dialog = selectfieldsdlg.selectFieldsDialog(fieldNames, self)

		if self.itSelectedFields is not None:
			dialog.setSelected(self.itSelectedFields)

		if dialog.exec_():
			self.itSelectedFields = dialog.getSelected()
			self.updateInfo()

	def mkWarn(self, msg):
		"""Orange color"""
		bgColor = "235,115,49"
		self.mkTable(bgColor, "WARNING", msg)

	def mkError(self, msg):
		"""Red color"""
		bgColor = "226,8,0"
		self.mkTable(bgColor, "ERROR", msg)

	def mkSuccess(self, msg):
		"""Green color"""
		bgColor = "55,164,44"
		self.mkTable(bgColor, "SUCCESS", msg)

	def mkInfo(self, msg):
		"""Blue color"""
		bgColor = "0,87,174"
		self.mkTable(bgColor, "INFO", msg)

	def mkTable(self, bgColor, status, msg):
		"""Formats message displayed in the log window."""
		formatStatus = ('<font style="color:rgb({0})"><strong>{1}</strong>'
					'</font>'.format(bgColor, status))
		self.logBrowser.append("{0}: {1}".format(formatStatus, msg))

	def okToContinue(self):
		"""Check before closing."""
		if len(self.updatedStrains):
			reply = QMessageBox(QMessageBox.Question,
			"Selection", "Entry selection in Bionumerics",
			QMessageBox.NoButton, self)

			originalButton = QPushButton("Keep Original Selection")
			updatedButton = QPushButton("Updated Items Only")
			cancelButton = QPushButton("Cancel")

			reply.addButton(originalButton, QMessageBox.ActionRole)
			reply.addButton(updatedButton, QMessageBox.ActionRole)
			reply.addButton(cancelButton, QMessageBox.RejectRole)
			reply.exec_()

			if reply.clickedButton() == cancelButton:
				return False
			elif reply.clickedButton() == originalButton:
				bn.selectEntries(self.selectedIds.values() +\
								 self.errorIds.keys())
			elif reply.clickedButton() == updatedButton:
				bn.selectEntries(self.updatedStrains)
		return True

	def populateTable(self):
		"""Populates table with data from ItemTracker."""
		self.selectedWidget.clear()
		self.selectedWidget.setSortingEnabled(False)
		numRows = len(self.tableResults)
		self.mkInfo("Selected items in ItemTracker: {0}".format(numRows))

		self.selectedWidget.setAlternatingRowColors(True)
		header = ["ItemID", "StrainID", "ItemType", "ItemName", "BacteriaItemID"]
		self.selectedWidget.setColumnCount(len(header))
		self.selectedWidget.setHeaderLabels(header)

		# use result and populate table
		for result in self.tableResults:
			properties = [unicode(i) for i in result]
			item = QTreeWidgetItem(self.selectedWidget, properties)
			item.setCheckState(0, Qt.Unchecked)

		self.selectedWidget.setSortingEnabled(True)
		for i in range(len(header)):
			self.selectedWidget.resizeColumnToContents(i)
		self.stackedWidget.setCurrentIndex(1) # switch view to table
		self.statusbar.clearMessage()
		self.populatedTable = True
		self.updateUi()

	def populateTree(self):
		"""Populates tree view with information from ItemTracker."""
		if len(self.errorIds):
			self.mkError("{0} entries do not have valid "
			"ItemTracker IDs in Bionumerics.".format(len(self.errorIds)))

			for key, msg in self.errorIds.iteritems():
				self.mkError("KEY: {0} {1}".format(key, msg))

		if not len(self.selectedIds):
			self.statusbar.showMessage("No items to process", 5000)
			return

		parents = {}
		headers = ["Items", "Selected", "SelectedBy", "Viability", "Volume",
				 "DNA concentration", "UserName", "TubePresent", "InputDate",
				 "AlternID", "Status"]

		self.treeWidget.setItemsExpandable(True)
		self.treeWidget.setAlternatingRowColors(True)
		self.treeWidget.setColumnCount(len(headers))
		self.treeWidget.setHeaderLabels(headers)

		msg = "Getting information from ItemTracker. Please wait..."
		self.statusbar.showMessage(msg)

		self.progressBar.setMinimum(0)
		self.progressBar.setMaximum(0)
		self.progressBar.show()

		(treeData, self.itemProperties,
		 message) = lims.GetDictionary((self.selectedIds.keys()))

		if len(message):
			for msg in message:
				self.mkError("ItemTracker error: {0}".format(msg))

		if not len(treeData):
			self.mkError("Could not get data from ItemTracker for"
						"selected entries")
			self.statusBar().clearMessage()
			self.progressBar.hide()
			self.updateUi()
			return

		# bugfix: If ItemType property does not exist for the first item
		# self.database is not set and tree view is not updated.
		db = None
		if not self.database:
			for item in self.itemProperties.values():
				try:
					db = item["ItemType"]
				except KeyError:
					pass

				if db == "Salmonella":
					self.database = db
					break
				elif db == "Listeria":
					self.database = db
					break

		self.progressBar.setMaximum(len(treeData))
		count = 0
		for key, value  in treeData.iteritems():
			count += 1
			self.progressBar.setValue(count)
			if not(value and isinstance(value, dict)):
				self.mkWarn("No data returned for key {0}".format(key))
				continue

			items = {}
			items[key] = value
			for results in self.getData(items, key):
				parent = parents.get(results[0])

				if not parent:
					parent_id = self.selectedIds[results[0]]
					self.strainInfo[parent_id] = {self.database:[],
												"Frozen Stock":[], "DNA":[]}
					parent = QTreeWidgetItem(self.treeWidget,
					[unicode(parent_id)])

					brush = QBrush()
					brush.setColor(Qt.blue)
					parent.setForeground(0, brush)
					parent.setIcon(0, QIcon(":/branch-closed.png"))
					parent.setData(0, Qt.CheckStateRole, QVariant())
					parents[results[0]] = parent

				for children in results[1]:
					itemName = self.itemProperties[children]["ItemName"]
					if not self.itemIds.get(itemName):
						self.itemIds[itemName] = children

					childprops = []
					childprops.append(unicode(itemName))

					for header in headers[1:]:
						try:
							childprop = self.itemProperties[children][header]

							if childprop is None or childprop == "":
								childprops.append(unicode(""))
							else:
								childprops.append(unicode(childprop))
						except KeyError:
							childprops.append(unicode(""))
							continue

					childs = parents.get(children)
					if not childs:
						childs = QTreeWidgetItem(parent, childprops)

						if self.itemProperties[children]["TubePresent"] == "-":
							childs.setBackgroundColor(0, QColor(232, 87, 82))
							childs.setForeground(0, QColor(255, 255, 255))

						if self.itemProperties[children]["Selected"] == "yes":
							childs.setBackgroundColor(0, QColor(119, 183, 83))
							childs.setForeground(0, QColor(255, 255, 255))

						itype = self.itemProperties[children]["ItemType"]
						if itype:
							self.strainInfo[parent_id][itype].append(itemName)
						parents[children] = childs
					childs.setCheckState(0, Qt.Unchecked)

		self.treeWidget.expandAll()
		for i in range(len(headers)):
			self.treeWidget.resizeColumnToContents(i)
		if not self.treeWidget.isEnabled():
			self.treeWidget.setEnabled(True)
		self.mkInfo("Processed <b>{0}</b> entries".format(len(treeData)))

		self.progressBar.setValue(len(treeData))
		self.progressBar.hide()
		self.populatedTree = True
		self.updateUi()
		self.statusbar.showMessage("Ready", 5000)

	def selectAll(self):
		"""All items are selected (checked)."""
		index = self.stackedWidget.currentIndex()
		widget = self.getWidget()
		it = QTreeWidgetItemIterator(widget, QTreeWidgetItemIterator.NotChecked)
		count = 0
		if index == 0:
			while it.value():
				if it.value().parent():
					it.value().setCheckState(0, Qt.Checked)
					count += 1
				it += 1
		elif index == 1:
			while it.value():
				it.value().setCheckState(0, Qt.Checked)
				count += 1
				it += 1
		if count:
			self.statusbar.showMessage("Selected {0} items".format(count), 3000)

	def selectDNA(self):
		"""Select all DNA items."""
		self.selectItems("DNA")

	def selectFrozenStock(self):
		"""Select all Frozen Stock items."""
		self.selectItems("Frozen Stock")

	def selectNone(self):
		"""Clears the selection."""
		widget = self.getWidget()
		it = QTreeWidgetItemIterator(widget, QTreeWidgetItemIterator.Checked)
		while it.value():
			it.value().setCheckState(0, Qt.Unchecked)
			it += 1

	def selectInvert(self):
		"""Inverts the selection."""
		index = self.stackedWidget.currentIndex()
		widget = self.getWidget()
		it = QTreeWidgetItemIterator(widget)

		if index == 0:
			while it.value():
				if it.value().parent():
					if it.value().checkState(0) == Qt.Checked:
						it.value().setCheckState(0, Qt.Unchecked)
					else:
						it.value().setCheckState(0, Qt.Checked)
				it += 1
		else:
			while it.value():
				if it.value().checkState(0) == Qt.Checked:
					it.value().setCheckState(0, Qt.Unchecked)
				else:
					it.value().setCheckState(0, Qt.Checked)
				it += 1

	def selectItems(self, itemType):
		"""Select all items of a given ItemType."""
		self.statusbar.showMessage("Selecting all {0}'s. "
								"Please wait...".format(itemType))

		items = []
		itemsAll = []
		index = self.stackedWidget.currentIndex()

		if index == 0:
			position = 0
			items = [item[itemType] for item in self.strainInfo.values()]
			for item in items:
				if len(item):
					itemsAll += item
		else:
			position = 3
			for item in self.tableResults:
				if item[2] == itemType:
					itemsAll.append(item[3])

		if not len(itemsAll):
			self.statusbar.showMessage("No {0}'s in list".format(itemType), 5000)
			return
		self.selectNone()
		widget = self.getWidget()
		it = QTreeWidgetItemIterator(widget)
		while it.value():
			if it.value().text(position) in itemsAll:
				it.value().setCheckState(0, Qt.Checked)
			it += 1
		self.statusbar.showMessage("Selected {0} {1}'s".format(len(itemsAll),
															 itemType), 3000)

	def selectInBionumerics(self, on):
		"""Selects Bionumerics entries with checked items from table view
		(get all selected)

		"""
		actionGroup = QActionGroup(self)
		actionGroup.addAction(self.actionViewTree)
		actionGroup.addAction(self.refresh_action)
		actionGroup.addAction(self.actionSelectAll)
		actionGroup.addAction(self.actionSelectInvert)
		actionGroup.addAction(self.actionSelectNone)
		actionGroup.addAction(self.actionSelectDNA)
		actionGroup.addAction(self.actionSelectFrozenStock)

		if on:
			actionGroup.setEnabled(False)
			if not len(self.itemNames):
				self.itemNames = bn.createIdMap()

			it = QTreeWidgetItemIterator(self.selectedWidget,
										 QTreeWidgetItemIterator.Checked)
			checkedItems = []
			while it.value():
				parentCode = unicode(it.value().text(4))
				bnStrain = self.itemNames[int(parentCode)]

				if bnStrain not in checkedItems:
					checkedItems.append(bnStrain)
				it += 1

			if len(checkedItems):
				bn.selectEntries(checkedItems)
			else:
				self.statusbar.showMessage("No items checked", 3000)
		else:
			actionGroup.setEnabled(True)
			bn.selectEntries(self.selectedIds.values() + self.errorIds.keys())

	def updateSelection(self):
		"""Updates selection status in ItemTracker."""
		if self.actionSelectInBionumerics.isChecked():
			self.selectInBionumerics(False)
			self.actionSelectInBionumerics.setChecked(False)

		self.updateButton.setEnabled(False)
		self.statusbar.showMessage("Updating selection. Please wait...")

		if self.selectRadioButton.isChecked():
			selectedAction = "SELECT"
		elif self.deselectRadioButton.isChecked():
			selectedAction = "DESELECT"

		checkedItems = {}
		updatedItems = []
		failedItems = []

		index = self.stackedWidget.currentIndex()
		widget = self.getWidget()
		it = QTreeWidgetItemIterator(widget, QTreeWidgetItemIterator.Checked)

		if index == 0:
			while it.value():
				itemName = unicode(it.value().text(0))
				itemId = self.itemIds[itemName]
				checkedItems[itemName] = itemId
				parentItem = self.getParent(it.value())
				strain =  unicode(parentItem.text(0))
				if strain not in self.updatedStrains:
					self.updatedStrains.append(strain)
				it += 1
		elif index == 1:
			if not len(self.itemNames):
				self.itemNames = bn.createIdMap()

			while it.value():
				itemId = unicode(it.value().text(0))
				itemName = unicode(it.value().text(3))
				checkedItems[itemName] = int(itemId)

				parentCode = unicode(it.value().text(4))
				strain = self.itemNames[int(parentCode)]
				if strain not in self.updatedStrains:
						self.updatedStrains.append(strain)
				it += 1

		if not len(checkedItems):
			self.statusbar.showMessage("No items checked", 5000)
			self.updateButton.setEnabled(True)
			return

		for itemName, itemId in checkedItems.iteritems():
			if selectedAction == "SELECT":
				result = lims.SelectItem(itemId)
			elif selectedAction == "DESELECT":
				result = lims.UnselectItem(itemId)

			if not len(result):
				updatedItems.append(itemName)
			else:
				failedItems.append(itemName)

		if len(updatedItems):
			self.mkSuccess("{0}ED {1} items".format(selectedAction,
												 len(updatedItems)))
			self.logBrowser.append("{0}".format(", ".join(updatedItems)))
			self.logger.info("{0}\t{1}".format(selectedAction, ", ".join(updatedItems)))
		if len(failedItems):
			self.mkError("{0} failed for {1} items".format(selectedAction,
														 len(failedItems)))

			self.logBrowser.append("{0}".format(", ".join(failedItems)))
			self.logger.info("{0}\t{1}".format(selectedAction,
											 ", ".join(failedItems)))

		self.updateButton.setEnabled(True)
		if len(updatedItems) or len(failedItems):
			self.populatedTree = False
			self.populatedTable = False
			self.refresh()

	def updateUi(self):
		"""Updates interface based on the view."""
		index = self.stackedWidget.currentIndex()

		# only show export actions in cherry picking
		if index != 2:
			widgets = [self.exportToolBar, self.exportActions]
			self.disableWidgets(widgets)
			for widget in widgets:
				widget.setVisible(False)

		# disable select menu in cherry picking (not implemented)
		if index == 2:
			self.selectMenu.setEnabled(False)
		else:
			self.selectMenu.setEnabled(True)

		if index == 0:  # Tree View
			self.disableWidgets([self.actionViewTree,
								self.actionSelectInBionumerics])
			self.enableWidgets([self.actionGetAllSelected,
							self.actionCherryPicking])

			for widget in [self.actionSelectInBionumerics,
						self.getSelectedToolBar]:
				widget.setVisible(False)

			#self.fieldsGroupBox.setVisible(True)
			widgets = [self.widget, self.treeWidget, self.selectGroupBox,
					self.fieldsGroupBox, self.actionLegend, self.treeToolBar,
					self.treeActions, self.selectActions]
			for widget in widgets:
				if not widget.isVisible():
					widget.setVisible(True)

			if self.populatedTree:
				self.enableWidgets(widgets)
			else:
				self.disableWidgets(widgets)

			try:
				self.treeWidget.selectedItems()[0]
			except IndexError:
				self.infoBrowser.setDisabled(True)

			self.fieldsGroupBox.setEnabled(self.infoBrowser.isEnabled())

		elif index == 1:
			self.widget.setVisible(True)
			self.enableWidgets([self.actionViewTree, self.actionCherryPicking])
			self.actionSelectInBionumerics.setVisible(True)
			self.getSelectedToolBar.setVisible(True)

			for widget in [self.actionLegend, self.fieldsGroupBox,
						 self.treeToolBar, self.treeActions]:
				widget.setVisible(False)

			self.disableWidgets([self.actionGetAllSelected, self.actionLegend,
								 self.treeToolBar, self.treeActions])

			widgets = [self.widget, self.selectedWidget, self.selectGroupBox,
					self.actionSelectInBionumerics, self.getSelectedToolBar,
					self.selectActions]

			if self.populatedTable:
				self.enableWidgets(widgets)
			else:
				self.disableWidgets(widgets)

		elif index == 2:
			self.widget.setVisible(False)  # ItemTracker and field selection
			self.actionCherryPicking.setEnabled(False)
			self.exportToolBar.setVisible(True)
			self.exportActions.setVisible(True)

			for action in [self.actionViewTree, self.actionGetAllSelected]:
				action.setEnabled(True)

			widgets = [self.selectActions, self.actionSelectInBionumerics,
					 self.actionLegend, self.treeActions, self.treeToolBar,
					 self.getSelectedToolBar]
			self.disableWidgets(widgets)
			for widget in widgets:
				widget.setVisible(False)

			widgets = [self.cherryView, self.filterGroupBox, self.lcdGroupBox,
					 self.exportActions, self.exportToolBar]

			if self.populatedCherry:
				self.enableWidgets(widgets)
			else:
				self.disableWidgets(widgets)

	def updateInfo(self):
		"""Infobar displaying ItemTracker and Bionumerics fields."""
		content = ('<table border="0" cellspacing="0" '
		'cellpadding="5" width="100%">')
		self.infoBrowser.clear()
		try:
			selected = self.treeWidget.selectedItems()[0]
		except IndexError:
			return
		else:
			self.infoBrowser.setEnabled(True)
			self.fieldsGroupBox.setEnabled(True)
		try:
			parentName = self.getParent(selected).text(0)
		except AttributeError:
			parentName = None

		if parentName:
			itemName = unicode(selected.text(0))
			itemId = self.itemIds[itemName]

			if itemId:
				content += """\
				<tr bgcolor="#85026C">
					<th colspan="2" align="left">
						<font color="white">ITEMTRACKER</font>
					</th>
				</tr>\
				"""
				count = 0
				for field, value in (("Strain", parentName),
									 ("Item&nbsp;Name", itemName),
									 ("Item&nbsp;ID", itemId)):
					if count % 2 == 0:
						content += """\
						<tr>
							<td>{0}</td>
							<td>{1}</td>
						</tr>\
						""".format(field, value)
					else:
						content += """\
						<tr bgcolor="#eee">
							<td>{0}</td>
							<td>{1}</td>
						</tr>\
						""".format(field, value)
					count += 1
			try:
				properties = self.itemProperties[int(itemId)]
			except KeyError:
				self.mkWarn("Could not get properties for "
				"ItemTracker ID {0}".format(itemId))

			if len(properties):
				try:
					location = properties["Position"]
				except KeyError:
					location = []
				if len(location):
					for field, value in (("Freezer", location[0]),
										 ("Rack", location[1]),
										 ("Shelf", location[2]),
										 ("Plate Rack", location[3]),
										 ("Position", location[4])):
						if count % 2 == 0:
							content += """\
							<tr>
								<td>{0}</td>
								<td>{1}</td>
							</tr>\
							""".format(field, value)
						else:
							content += """\
							<tr bgcolor="#eee">
								<td>{0}</td>
								<td>{1}</td>
							</tr>\
							""".format(field, value)
						count += 1

				if len(self.itSelectedFields):

					for itField in self.itSelectedFields:
						try:
							itemProperty = properties[itField]
						except KeyError:
							itemProperty = ""

						if count % 2 == 0:
							content += """\
							<tr>
								<td>{0}</td>
								<td>{1}</td>
							</tr>\
							""".format(itField, itemProperty)
						else:
							content += """\
							<tr bgcolor="#eee">
								<td>{0}</td>
								<td>{1}</td>
							</tr>\
							""".format(itField, itemProperty)
						count += 1
			else:
				content += """\
				<tr>
					<td colspan="2">No information</td>
				</tr>"""

			self.infoBrowser.setHtml(QString(content))
			content += """\
			<tr bgcolor="#CF4913">
				<th colspan="2" align="left">
					<font color="white">BIONUMERICS</font>
				</th>
			</tr>\
			"""
			strainInfo = {}
			try:
				strainInfo = self.bnFields.get(unicode(parentName))
			except KeyError:
				self.mkWarn("Could not get information for {0}".format(parentName))

			if len(strainInfo):
				count = 0
				for field in self.bnSelectedFields:

					if count % 2 == 0:
						content += """\
						<tr>
							<td>{0}</td>
							<td>{1}</td>
						</tr>\
						""".format(field, strainInfo[field])
					else:
						content += """\
						<tr bgcolor="#eee">
							<td>{0}</td>
							<td>{1}</td>
						</tr>\
						""".format(field, strainInfo[field])
					count += 1
			else:
				self.mkWarn("No information for {0}".format(parentName))
			content += "</table>"
		else:
			strainName = unicode(selected.text(0))
			itemId = None
			for ids, keys in self.selectedIds.iteritems():
				if keys == strainName:
					itemId = ids
					break
			if not itemId:
				self.infoBrowser.setHtml(QString(content))
				return

			content = """\
			<table border="0" cellpadding="5" cellspacing="0" width="100%">
				<tr bgcolor="#85026C">
					<th colspan="2" align="left">
						<font color="white">ITEMTRACKER</font>
					</th>
				</tr>
				<tr bgcolor="#eee">
					<td>AlternID</td>
					<td>{0}</td>
				</tr>
				<tr>
					<td>OriginalID</td>
					<td>{1}</td>
				</tr>\
				""".format(self.itemProperties[itemId]["AlternID"],
			self.itemProperties[itemId]["OriginalID"])

			content += "</table>"
			content += """\
			<table border="0" cellpadding="5" cellspacing="0" width="100%">
				<tr bgcolor="#BF0361">
					<th align="left">
						<font color="white">{0}</font>
					</th>
					<th align="right">
						<font color="white">{1}</font>
					</th>
				</tr>
				<tr>
					<td colspan="2">{2}</td>
				</tr>\
				""".format(self.database.upper(),
				len(self.strainInfo[strainName][self.database]),
				", ".join(self.strainInfo[strainName][self.database]))

			content += """\
			<tr bgcolor="#00438A">
				<th align="left">
					<font color="white">FROZEN STOCK</font>
				</th>
				<th align="right">
					<font color="white">{0}</font>
				</th>
			</tr>
			<tr>
				<td colspan="2">{1}</td>
			</tr>\
			""".format(len(self.strainInfo[strainName]["Frozen Stock"]),
			", ".join(self.strainInfo[strainName]["Frozen Stock"]))

			content += """\
			<tr bgcolor="#00734D">
				<th align="left">
					<font color="white">DNA</font>
				</th>
				<th align="right">
					<font color="white">{0}</font>
				</th>
			</tr>
			<tr>
				<td colspan="2">{1}</td>
			</tr>\
			""".format(len(self.strainInfo[strainName]["DNA"]),
			", ".join(self.strainInfo[strainName]["DNA"]))

			content += "</table>"
		self.infoBrowser.setHtml(QString(content))

	def viewTree(self):
		"""Toolbar button/action to switch to tree view."""
		self.selectRadioButton.setChecked(True)
		if not self.populatedTree:
			self.stackedWidget.setCurrentIndex(0)
			self.refresh()
		self.stackedWidget.setCurrentIndex(0)
		self.updateUi()

	def refresh(self):
		"""Updates view(s)."""
		index = self.stackedWidget.currentIndex()
		if index == 1:
			self.populatedTable = False
			self.selectedWidget.clear()
			self.getAllSelected()
		elif index == 0:
			self.populatedTree = False
			self.treeWidget.clear()
			self.treeWidget.setDisabled(True)
			bnField = "ItemTracker ID"
			self.selectedIds = {}
			self.errorIds = {}
			selection = DB.Db.Selection
			self.selectedIds, self.errorIds = bn.getItemIds(bnField, selection)
			if len(self.selectedIds):
				self.strainInfo = {}
				self.itemIds = {}
				self.getBnFields()
#			self.populateTree()
			QTimer.singleShot(0, self.populateTree)
		elif index == 2:
			self.populatedCherry = False
			QTimer.singleShot(0, self.cherryPicking)

		self.updateUi()


def main():
	"""Main function."""
	sys.__dict__["argv"] = ["argv"]
	app = QApplication(sys.argv)
	app.setOrganizationName("LabAchtman")
	app.setOrganizationDomain("ucc.ie")
	app.setApplicationName("IT Query")
	app.setWindowIcon(QIcon(":/logo.png"))

	dbField = "ItemTracker ID"
	fields = [field.Name for field in DB.Db.Fields]

	if dbField in fields:
		selection = DB.Db.Selection
		ids, errIds = bn.getItemIds(dbField, selection)
		form = Form(ids, errIds)
		form.show()
		app.exec_()
	else:
		msg = "The field <b>{0}</b> must be present in the database for the program \
		to work.".format(dbField)
		QMessageBox.critical(None, "Field absent", msg)
	del app
	__bnscontext__.Stop()

if __name__ == "__main__":
	main()
