# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIs\CoMPlEx_zPath_Dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_zPath_dialog(object):
    def setupUi(self, zPath_dialog):
        zPath_dialog.setObjectName("zPath_dialog")
        zPath_dialog.resize(742, 597)
        self.horizontalLayout = QtWidgets.QHBoxLayout(zPath_dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.zPathPlot = PlotWidget(zPath_dialog)
        self.zPathPlot.setObjectName("zPathPlot")
        self.horizontalLayout.addWidget(self.zPathPlot)
        self.buttonBox = QtWidgets.QDialogButtonBox(zPath_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)

        self.retranslateUi(zPath_dialog)
        self.buttonBox.accepted.connect(zPath_dialog.accept)
        self.buttonBox.rejected.connect(zPath_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(zPath_dialog)

    def retranslateUi(self, zPath_dialog):
        _translate = QtCore.QCoreApplication.translate
        zPath_dialog.setWindowTitle(_translate("zPath_dialog", "Z piezo path"))

from pyqtgraph import PlotWidget
