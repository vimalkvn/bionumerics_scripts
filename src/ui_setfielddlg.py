# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\ui\setfielddlg.ui'
#
# Created: Fri Jul 09 15:55:54 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(259, 159)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setLineWidth(2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.value_line_edit = QtGui.QLineEdit(Dialog)
        self.value_line_edit.setMaxLength(80)
        self.value_line_edit.setObjectName("value_line_edit")
        self.gridLayout.addWidget(self.value_line_edit, 1, 1, 1, 1)
        self.field_combo_box = QtGui.QComboBox(Dialog)
        self.field_combo_box.setObjectName("field_combo_box")
        self.gridLayout.addWidget(self.field_combo_box, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 18, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.apply_button = QtGui.QPushButton(Dialog)
        self.apply_button.setObjectName("apply_button")
        self.horizontalLayout.addWidget(self.apply_button)
        self.close_button = QtGui.QPushButton(Dialog)
        self.close_button.setObjectName("close_button")
        self.horizontalLayout.addWidget(self.close_button)
        self.deselect_button = QtGui.QPushButton(Dialog)
        self.deselect_button.setObjectName("deselect_button")
        self.horizontalLayout.addWidget(self.deselect_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Set Field", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Sets the value for chosen field name.\n"
"Entries must be selected in Bionumerics", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Field", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.value_line_edit.setToolTip(QtGui.QApplication.translate("Dialog", "80 characters maximum", None, QtGui.QApplication.UnicodeUTF8))
        self.apply_button.setText(QtGui.QApplication.translate("Dialog", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.close_button.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.deselect_button.setText(QtGui.QApplication.translate("Dialog", "Deselect All", None, QtGui.QApplication.UnicodeUTF8))

