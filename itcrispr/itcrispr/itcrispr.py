"""Iterate for CRISPR sequences"""
import bns  # IGNORE:F0401 @UnresolvedImport
import os
import sys

try:
	import bnpyqt  # IGNORE:W0611 @UnusedImport
except ImportError:
	sys.exit("Could not import PyQt")

from PyQt4.QtCore import (Qt, QTimer, QSettings, QVariant, QSize, QPoint,
						QFile, QFileInfo, QTextStream)
from PyQt4.QtGui import (QApplication, QMainWindow, QListWidgetItem,
						QMessageBox, QIcon, QFileDialog)
import copy
import time
import ConfigParser
import bn
import dbms
import primers
from xml.etree import ElementTree as ET
from ui import ui_mainwindow

__version__ = "0.1.4"

# Bionumerics database
BNDB = bns.Database.Db.Info.Name
BNDB_PATH = bns.Database.Db.Info.Path
# Database to store trace information
DB = os.path.join(BNDB_PATH, "{0}.sqlite".format(BNDB))

# Configuration variables and their types
CFG_DEFS = {"DATABASES": {"type": "list", "value": []},
		"EXPERIMENTS": {"type": "list", "value": []},
		"EXTENSION": {"type": "string", "value": ""},
		"PRIMER_PATH": {"type": "string", "value": ""}
		}


class Window(QMainWindow, ui_mainwindow.Ui_MainWindow):
	"""Main Window"""

	def __init__(self, key, exper, asm, primer_data=None, parent=None):
		"""Requires key, experiment, an opened assembly window and primers
		dictionary of the format

		primer_data = {primer_name: {"status": "Repeat", "position": (10, 40)}}

		"""
		super(Window, self).__init__(parent)
		self.setupUi(self)
		self.setWindowTitle("Iterate CRISPR {0}".format(__version__))
		if primer_data is None:
			primer_data = {}
		self.primer_data = primer_data
		self.key = key
		self.exper = exper
		self.keyLabel.setText(key)
		self.experLabel.setText(exper)
		self.asm = asm

		self.stopButton.clicked.connect(stop)
		self.skipButton.clicked.connect(self.close)
		self.selectAllButton.clicked.connect(self.selectAll)
		self.selectNoneButton.clicked.connect(self.selectNone)
		self.finishedButton.clicked.connect(self.saveFinished)
		self.unfinishedButton.clicked.connect(self.saveUnfinished)
		self.recalculateButton.clicked.connect(self.recalculate)
		self.exportButton.clicked.connect(self.exportDatabase)
		self.listWidget.itemChanged.connect(self.itemChanged)

		for content in self.primer_data.keys():
			item = QListWidgetItem(content, self.listWidget)
			if self.primer_data[content]["status"] == "Repeat":
				item.setCheckState(Qt.Checked)
			else:
				item.setCheckState(Qt.Unchecked)
		self.listWidget.itemDoubleClicked.connect(self.selectInAssembler)

		# restore main window state
		settings = QSettings()
		size = settings.value("Window/Size", QVariant(QSize(600, 500))).toSize()
		self.resize(size)
		position = settings.value("Window/Position",
								QVariant(QPoint(0, 0))).toPoint()
		self.move(position)
		self.restoreState(settings.value("Window/State").toByteArray())
		QTimer.singleShot(6000, self.hideHint)

	def closeEvent(self, event):
		"""Called on closing the window. Save settings and exit."""
		settings = QSettings()
		settings.setValue("Window/Size", QVariant(self.size()))
		settings.setValue("Window/Position", QVariant(self.pos()))
		settings.setValue("Window/State", QVariant(self.saveState()))

	def exportDatabase(self):
		"""Export entire traces database in CSV format."""
		con, cur = dbms.connect(DB)

		# get column names - sqlite only
		cur.execute("PRAGMA table_info(traces)")
		cols = cur.fetchall()
		header = ", ".join([str(col[1]) for col in cols])

		data = []
		for row in cur.execute("select * from traces"):
			data.append(", ".join(str(item) for item in row))
		con.close()

		if not len(data):
			self.statusBar().showMessage("No data to write", 3000)
			return

		export_path = os.path.join(BNDB_PATH, "Export")
		if not os.path.exists(export_path):
			os.mkdir(export_path)

		fh = QFileDialog.getSaveFileName(self, "Export Database", export_path,
										"Text files (*.txt);;All Files (*.*)")
		if not fh:
			self.statusBar().showMessage("Cancelled database export.", 3000)
			return

		if QFileInfo(fh).suffix().isEmpty():
			fh += ".txt"

		fname = QFile(fh)
		if fname.open(QFile.WriteOnly | QFile.Text):
			txt = QTextStream(fname)
			txt << "{0}\n".format(header)  # IGNORE:W0106
			txt << "\n".join(item for item in data)  # IGNORE:W0106
			self.statusBar().showMessage("Database export complete", 5000)
			QMessageBox.information(self, "Information",
								("Database exported to: "
								"<p><font color='blue'>{0}</blue>"
								"</p>".format(str(fname.fileName()))))

	def hideHint(self):
		"""Hide hint after 6 seconds"""
		self.hintLabel.hide()
		self.hintText.hide()

	def hasCheckedItems(self):
		"""If any primers are checked return True. If no primers are checked,
		return False

		"""
		for i in range(self.listWidget.count()):
			item = self.listWidget.item(i)
			if item.checkState() == Qt.Checked:
				return True
		return False

	def itemChanged(self):
		"""Toggles 'Save as Finished' and 'Save as Unfinished' buttons

		If there are items checked, finished button should be disabled
		If no items are checked, unfinished button should be disabled

		"""
		if self.hasCheckedItems():
			self.finishedButton.setDisabled(True)
			self.finishedButton.setToolTip("Please deselect all primers")
			self.unfinishedButton.setToolTip("")
			self.unfinishedButton.setEnabled(True)
		else:
			self.unfinishedButton.setDisabled(True)
			self.unfinishedButton.setToolTip("Please select primers")
			self.finishedButton.setEnabled(True)
			self.finishedButton.setToolTip("")

	def setState(self, state):
		"""Set checked state of primers in list widget"""
		for i in range(self.listWidget.count()):
			item = self.listWidget.item(i)
			item.setCheckState(state)

	def selectAll(self):
		"""Check all primers"""
		self.setState(Qt.Checked)

	def selectNone(self):
		"""Remove all checks"""
		self.setState(Qt.Unchecked)

	def saveFinished(self):
		"""Save experiment for key as finished in the traces database"""
		con, cur = dbms.connect(DB)
		sql = "select id from traces where key=? and gene=? and database=?"
		params = [self.key, self.exper, BNDB]
		errmsg = dbms.execute(cur, sql, params)
		if errmsg:
			con.close()
			msg = ("Couldn't retrieve id from traces table for Key {0} "
				"and Gene {1}<br>{2}".format(self.key, self.exper, errmsg))
			QMessageBox.critical(self, "Error", msg)
			return

		result = cur.fetchall()
		if len(result) > 0:
			params = tuple([item[0] for item in result])
			sql = ("delete from traces where id "
				"in ({0})".format(",".join("?" for item in params)))

			errmsg = dbms.execute(cur, sql, params)
			if errmsg:
				msg = ("Could not delete traces with ids {0}"
					"<br>{1}.<br> I quit!. Proceeding will create "
					"duplicates".format(",".join(params), errmsg))
				QMessageBox.critical(self, "Error", msg)
				con.rollback()
				con.close()
				return

		sql = ("insert into traces(key, gene, database, username, "
			"date, status) values(?,?,?,?,?,?)")
		params = (self.key, self.exper, BNDB, os.environ.get("USERNAME"),
				time.asctime(), "Finished")

		errmsg = dbms.execute(cur, sql, params)
		if errmsg:
			con.rollback()
			con.close()
			msg = ("Could not save experiment as finished"
				"<br>{0}".format(errmsg))
			QMessageBox.critical(self, "Error", msg)
			return
		con.commit()
		con.close()
		self.asm.ProjectStatus = 1
		self.asm.Save()
		self.close()

	def saveUnfinished(self):
		"""Save key, experiment, selected primers as unfinished in the traces
		database.

		"""
		con, cur = dbms.connect(DB)
		errmsg = dbms.execute(cur,
						("select id, primer from traces where key=? and "
						"gene=? and database=?"), [self.key, self.exper, BNDB])
		if errmsg:
			con.close()
			msg = ("Could not get ids from traces<br>{0}".format(errmsg))
			QMessageBox.critical(self, "Error", msg)
			return

		result = cur.fetchall()
		result = dict(result)
		inserts = []
		deletes = []
		for i in range(self.listWidget.count()):
			item = self.listWidget.item(i)
			checkState = item.checkState()
			primer = unicode(item.text())

			# Checked in the list, not in database, insert it
			if (primer not in result.values()) and (checkState == Qt.Checked):
				inserts.append(primer)

			# Present in database and unchecked, remove
			if (primer in result.values()) and (checkState == Qt.Unchecked):
				for primer_id, value in result.iteritems():
					if value == primer:
						deletes.append(primer_id)
						break
		# nothing to do, return
		if not (len(inserts) or len(deletes)):
			con.close()
			self.asm.ProjectStatus = 0
			self.asm.Save()
			self.close()
			return

		if len(inserts):
			cols = ["key", "gene", "database", "username", "date",
				"status", "primer"]
			sql = ("insert into traces({0}) "
				"values({1})".format(", ".join(cols),
									",".join("?" for item in cols)))
			params = []
			for primer in inserts:
				params.append([self.key, self.exper, BNDB,
							os.environ.get("USERNAME"), time.asctime(),
							"Repeat", primer])

			if len(inserts) > 0:
				errmsg = dbms.execute(cur, sql, params, executemany=True)
			else:
				errmsg = dbms.execute(cur, sql, params)

			if errmsg:
				con.rollback()
				msg = ("Error adding entries to cherry "
					"picking database<br>{0}".format(errmsg))
				QMessageBox.critical(self, "Error", msg)

		if len(deletes):
			errmsg = dbms.execute(cur, ("delete from traces where id in "
									"({0})".format(",".join("?" for item in
														deletes))), deletes)
			if errmsg:
				con.rollback()
				QMessageBox.critical(self, "Error",
									("Error removing entries from cherry"
									" picking database<br>{0}".format(errmsg)))
		con.commit()
		con.close()
		self.asm.ProjectStatus = 0
		self.asm.Save()
		self.close()

	def recalculate(self):
		"""Assemble again"""
		self.asm.Save()
		self.asm.AlignIncr()

	def selectInAssembler(self, item):
		"""Selects primer position (provided in init) in the assembler"""
		position = self.primer_data[unicode(item.text())]["position"]
		self.asm.ContigSelPosit = position


def stop():
	"""Exit program"""
	QApplication.exit(1)


def main(path, context):
	"""Main function"""
	# initial setup
	sys.__dict__["argv"] = [""]
	app = QApplication(sys.argv)
	app.setOrganizationName("LabAchtman")
	app.setOrganizationDomain("ucc.ie")
	app.setApplicationName("Iterate CRISPR")
	app.setWindowIcon(QIcon(":/logo.png"))

	Stop = context.Stop  # __bnscontext__.Stop
	# read configuration
	cfg = {"DATABASES": [], "EXPERIMENTS": [], "EXTENSION": "",
		"PRIMER_PATH": ""}

	cfg_file = os.path.join(path, "itcrispr", "itcrispr.cfg")
	cfg_loc = ("<br><br>The configuration file is at <br><br>"
			"<font color=blue>{0}</font>".format(cfg_file))
	config = ConfigParser.RawConfigParser()
	config.readfp(open(cfg_file))

	for item in cfg:
		value = ""
		try:
			value = config.get("configuration", item)
		except ConfigParser.NoOptionError:
			QMessageBox.critical(None, "Error", "<b>{0}</b> is not defined in "\
								"configuration file {1}".format(item, cfg_loc))
			Stop()
		if not len(value):
			QMessageBox.critical(None, "Error", "Cannot read <b>{0}</b> from "\
								"configuration file. "\
								"Is it defined? {1}".format(item, cfg_loc))
			Stop()
		if CFG_DEFS[item]["type"] == "string":
			cfg[item] = value
		elif CFG_DEFS[item]["type"] == "list":
			cfg[item] = value.split(",")

	if not BNDB in cfg["DATABASES"]:
		msg = """Sorry. I can only run inside the following databases.<br><br>\
		<strong>{0}</strong><br><br>
		If you are sure, please update the <b>DATABASES</b> section of the \
		configuration file using a text editor like this<br><br>\
		<b><code>DATABASES={0},{1}</code></b><br><br>\
		The configuration file is at <br><br>\
		<font color=blue>{2}</font>""".format(", ".join(cfg["DATABASES"]),
											BNDB, cfg_file)
		QMessageBox.information(None, "Information", msg)
		Stop()

	# get entries from BN to work with
	worklist = bn.getChecklist(cfg["EXPERIMENTS"])

	# rare, empty database, no experiment
	if not len(worklist):
		QMessageBox.information(None, "Information", "No entries to check")
		Stop()

	# create traces table if it does not exist
	dbms.create_traces_table(DB)
	con, cur = dbms.connect(DB)

	# make a list of finished entries in cherry picking database
	sql = "select key, gene from traces where database=? and status=?"
	params = [BNDB, "Finished"]

	errmsg = dbms.execute(cur, sql, params)
	if errmsg:
		msg = ("Could not retrieve data from cherry picking "
			"database<br>SQL: {0}<br>Params: {1}"
			"<br>{2}".format(sql, params, errmsg))
		QMessageBox.critical(None, "Error", msg)
		con.close()
		Stop()

	result = cur.fetchall()
	con.close()
	dbList = [list(item) for item in result]
	# ignore finished experiments
	checklist = copy.deepcopy(worklist)
	for key in worklist:
		for exper in worklist[key]:
			if [key, exper] in dbList:
				checklist[key].remove(exper)
		if not len(checklist[key]):
			checklist.pop(key)

	if not len(checklist):
		QMessageBox.information(None, "Information", "No entries to check")
		Stop()
	# load primer_data from directory
	primer_data, messages = primers.getPrimers(cfg["PRIMER_PATH"],
											cfg["EXTENSION"])
	# TODO: continue on duplicate primers
	if len(messages):
		msg = ("Error while reading primer files<br><br>{0}"
		"<br>".format("\n".join(messages)))
		if not len(primer_data):
			msg += ("Please check if correct primer path is "
			"defined in configuration file {0}".format(cfg_loc))
		QMessageBox.critical(None, "Warning", msg)
		Stop()

	asm = bns.Sequences.Assembly()
	# iterate over entries in check list
	stopped = 0
	for key in sorted(checklist):
		if stopped:
			break
		for exper in checklist[key]:
			# asm.Load(key, exper)
			asm.OpenWindow(key, exper)
			bn.deleteContigs(asm)

			# import all primer sequences
			seqdata = dict((item.Name, item) for item in asm.Sequences)
			for primer in primer_data:
				import_file = os.path.join(cfg["PRIMER_PATH"],
										"{0}.{1}".format(primer,
														cfg["EXTENSION"]))
				txtfile = os.path.basename(import_file)
				if not txtfile in seqdata:
					asmseq = asm.ImportSeq(import_file, "TXT")
				else:
					asmseq = seqdata[txtfile]
				asmseq.Status = 1
				asmseq.SetBaseStatus((0, len(asmseq.Sequence) - 1), 1)

			# set minimum score to the smallest length of the primer sequence
			min_score = min(len(item) for item in primer_data.values())
			element = ET.XML(asm.Settings)
			for subelement in element:
				if subelement.tag == "AlignSettings":
					# multiple of 100 for some reason!
					subelement.attrib["MinScore"] = str(min_score * 100)
			asm.Settings = ET.tostring(element)
			asm.Save()
			asm.AlignAll()
			asm.Contigs[0].AutoTrim()

			primer_files = ["{0}.{1}".format(item, cfg["EXTENSION"]) for
						item in primer_data.keys()]
			selected_primers = {}
			for i in range(len(asm.Sequences)):
				sequence = asm.Sequences[i]
				contig = sequence.GetContig()
				if not contig:
					continue
				if contig.contignr_ != 0:
					sequence.ContigRemove()  # TODO: also remove from assembly
					sequence.Status = 0
					continue
				if sequence.Name in primer_files:
					trim1, trim2 = sequence.Trimming
					tstart, tstop = (sequence.RawToContig(trim1),
					sequence.RawToContig(trim2))
					if tstart > tstop:
						region1, region2 = tstop, tstart
					else:
						region1, region2 = tstart, tstop

					seq_name = sequence.Name.split(".")[0]
					#get primer status
					sql = ("select status from traces where key=? "
						"and gene=? and database=? and primer=?")
					params = (key, exper, BNDB, seq_name)
					con, cur = dbms.connect(DB)
					errmsg = dbms.execute(cur, sql, params)
					if errmsg:
						msg = ("Could not find primer status from "
							"cherry picking database.<br> Key: {0}, "
							"Experiment: {1}, Primer {2}<br> will "
							"not be included!<br><br>"
							"{3}".format(key, exper, seq_name, errmsg))
						QMessageBox.warning(None, "Warning", msg)
						continue

					res = cur.fetchone()
					if res is not None:
						status = res[0]
					else:
						status = res
					selected_primers[seq_name] = {"status": status,
												"position": (region1, region2)}
					contig.AddRegion((region1, region2), sequence.Name,
									(1.0, 1.0, 0.5))  # yellow color
			asm.Save()
			window = Window(key, exper, asm, selected_primers)
			window.show()
			stopped = app.exec_()
			asm.Close()

			# if user does not want to continue
			if stopped:  # stopped becomes 1
				app.closeAllWindows()
				break
