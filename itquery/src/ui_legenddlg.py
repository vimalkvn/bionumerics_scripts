# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../ui/legenddlg.ui'
#
# Created: Tue Jan 25 10:21:36 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LegendDlg(object):
    def setupUi(self, LegendDlg):
        LegendDlg.setObjectName(_fromUtf8("LegendDlg"))
        LegendDlg.resize(178, 153)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(LegendDlg)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(LegendDlg)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.absent_label = QtGui.QLabel(self.frame)
        self.absent_label.setText(_fromUtf8(""))
        self.absent_label.setPixmap(QtGui.QPixmap(_fromUtf8(":/legend-absent.png")))
        self.absent_label.setObjectName(_fromUtf8("absent_label"))
        self.gridLayout.addWidget(self.absent_label, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.selected_label = QtGui.QLabel(self.frame)
        self.selected_label.setText(_fromUtf8(""))
        self.selected_label.setPixmap(QtGui.QPixmap(_fromUtf8(":/legend-selected.png")))
        self.selected_label.setObjectName(_fromUtf8("selected_label"))
        self.gridLayout.addWidget(self.selected_label, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.absent_selected_label = QtGui.QLabel(self.frame)
        self.absent_selected_label.setText(_fromUtf8(""))
        self.absent_selected_label.setPixmap(QtGui.QPixmap(_fromUtf8(":/legend-selected.png")))
        self.absent_selected_label.setObjectName(_fromUtf8("absent_selected_label"))
        self.gridLayout.addWidget(self.absent_selected_label, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(68, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.close_button = QtGui.QPushButton(LegendDlg)
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.horizontalLayout.addWidget(self.close_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.retranslateUi(LegendDlg)
        QtCore.QMetaObject.connectSlotsByName(LegendDlg)

    def retranslateUi(self, LegendDlg):
        LegendDlg.setWindowTitle(QtGui.QApplication.translate("LegendDlg", "Legend", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("LegendDlg", "Tube Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("LegendDlg", "Tube Absent, Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("LegendDlg", "Tube Absent", None, QtGui.QApplication.UnicodeUTF8))
        self.close_button.setText(QtGui.QApplication.translate("LegendDlg", "Close", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
