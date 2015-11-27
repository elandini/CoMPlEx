# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIs\CoMPlEx_zPath_Dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_zPath_dialog(object):
    def setupUi(self, zPath_dialog):
        zPath_dialog.setObjectName(_fromUtf8("zPath_dialog"))
        zPath_dialog.resize(742, 597)
        self.horizontalLayout = QtGui.QHBoxLayout(zPath_dialog)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.zPathPlot = PlotWidget(zPath_dialog)
        self.zPathPlot.setObjectName(_fromUtf8("zPathPlot"))
        self.horizontalLayout.addWidget(self.zPathPlot)
        self.buttonBox = QtGui.QDialogButtonBox(zPath_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)

        self.retranslateUi(zPath_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), zPath_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), zPath_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(zPath_dialog)

    def retranslateUi(self, zPath_dialog):
        zPath_dialog.setWindowTitle(_translate("zPath_dialog", "Z piezo path", None))

from pyqtgraph import PlotWidget
