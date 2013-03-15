# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\Python\itQuery\selectfieldsdlg.ui'
#
# Created: Wed Mar 31 16:48:53 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_selectFieldsDialog(object):
    def setupUi(self, selectFieldsDialog):
        selectFieldsDialog.setObjectName("selectFieldsDialog")
        selectFieldsDialog.resize(276, 243)
        self.horizontalLayout = QtGui.QHBoxLayout(selectFieldsDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.fieldListWidget = QtGui.QListWidget(selectFieldsDialog)
        self.fieldListWidget.setObjectName("fieldListWidget")
        self.verticalLayout.addWidget(self.fieldListWidget)
        self.buttonBox = QtGui.QDialogButtonBox(selectFieldsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(selectFieldsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), selectFieldsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), selectFieldsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(selectFieldsDialog)

    def retranslateUi(self, selectFieldsDialog):
        selectFieldsDialog.setWindowTitle(QtGui.QApplication.translate("selectFieldsDialog", "Select Fields", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    selectFieldsDialog = QtGui.QDialog()
    ui = Ui_selectFieldsDialog()
    ui.setupUi(selectFieldsDialog)
    selectFieldsDialog.show()
    sys.exit(app.exec_())

