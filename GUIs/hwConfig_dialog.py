# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ettore/GIT/CoMPlEx/GUIs/hwConfig_dialog.ui'
#
# Created: Fri Aug 21 18:17:34 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_hwConfig_dialog(object):
    def setupUi(self, hwConfig_dialog):
        hwConfig_dialog.setObjectName(_fromUtf8("hwConfig_dialog"))
        hwConfig_dialog.resize(531, 631)
        self.verticalLayout = QtGui.QVBoxLayout(hwConfig_dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(hwConfig_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(hwConfig_dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(hwConfig_dialog)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout.addWidget(self.groupBox_3)
        self.buttonBox = QtGui.QDialogButtonBox(hwConfig_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(3, 1)

        self.retranslateUi(hwConfig_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), hwConfig_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), hwConfig_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(hwConfig_dialog)

    def retranslateUi(self, hwConfig_dialog):
        hwConfig_dialog.setWindowTitle(_translate("hwConfig_dialog", "Hardware Config", None))
        self.groupBox.setTitle(_translate("hwConfig_dialog", "Connections", None))
        self.groupBox_2.setTitle(_translate("hwConfig_dialog", "Piezo settings", None))
        self.groupBox_3.setTitle(_translate("hwConfig_dialog", "Other", None))

