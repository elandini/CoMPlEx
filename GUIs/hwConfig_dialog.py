# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIs\hwConfig_dialog.ui'
#
# Created: Tue Sep 08 15:32:43 2015
#      by: PyQt4 UI code generator 4.9.6
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
        hwConfig_dialog.resize(531, 696)
        self.verticalLayout = QtGui.QVBoxLayout(hwConfig_dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(hwConfig_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.afmIpLine = QtGui.QLineEdit(self.groupBox)
        self.afmIpLine.setObjectName(_fromUtf8("afmIpLine"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.afmIpLine)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.afmSubPortNum = QtGui.QSpinBox(self.groupBox)
        self.afmSubPortNum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.afmSubPortNum.setMaximum(100000000)
        self.afmSubPortNum.setObjectName(_fromUtf8("afmSubPortNum"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.afmSubPortNum)
        self.label_14 = QtGui.QLabel(self.groupBox)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_14)
        self.afmPubPortNum = QtGui.QSpinBox(self.groupBox)
        self.afmPubPortNum.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.afmPubPortNum.setMaximum(100000000)
        self.afmPubPortNum.setObjectName(_fromUtf8("afmPubPortNum"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.afmPubPortNum)
        self.label_15 = QtGui.QLabel(self.groupBox)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_15)
        self.curveNameLine = QtGui.QLineEdit(self.groupBox)
        self.curveNameLine.setObjectName(_fromUtf8("curveNameLine"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.curveNameLine)
        self.label_16 = QtGui.QLabel(self.groupBox)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_16)
        self.monitNameLine = QtGui.QLineEdit(self.groupBox)
        self.monitNameLine.setObjectName(_fromUtf8("monitNameLine"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.monitNameLine)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_3)
        self.motorXyPortLine = QtGui.QLineEdit(self.groupBox)
        self.motorXyPortLine.setObjectName(_fromUtf8("motorXyPortLine"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.motorXyPortLine)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.label_4)
        self.motorZPortLine = QtGui.QLineEdit(self.groupBox)
        self.motorZPortLine.setObjectName(_fromUtf8("motorZPortLine"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.motorZPortLine)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(hwConfig_dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_5)
        self.maxPiezoVoltNumDbl = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.maxPiezoVoltNumDbl.setMinimum(-99.0)
        self.maxPiezoVoltNumDbl.setObjectName(_fromUtf8("maxPiezoVoltNumDbl"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.maxPiezoVoltNumDbl)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_6)
        self.minPiezoVoltNumDbl = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.minPiezoVoltNumDbl.setMinimum(-99.0)
        self.minPiezoVoltNumDbl.setObjectName(_fromUtf8("minPiezoVoltNumDbl"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.minPiezoVoltNumDbl)
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_7)
        self.maxPiezoExtNumDbl = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.maxPiezoExtNumDbl.setMinimum(-99.0)
        self.maxPiezoExtNumDbl.setObjectName(_fromUtf8("maxPiezoExtNumDbl"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.maxPiezoExtNumDbl)
        self.label_8 = QtGui.QLabel(self.groupBox_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_8)
        self.minPiezoExtNumDbl = QtGui.QDoubleSpinBox(self.groupBox_2)
        self.minPiezoExtNumDbl.setMinimum(-99.0)
        self.minPiezoExtNumDbl.setObjectName(_fromUtf8("minPiezoExtNumDbl"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.minPiezoExtNumDbl)
        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_9)
        self.farNearCmbBox = QtGui.QComboBox(self.groupBox_2)
        self.farNearCmbBox.setObjectName(_fromUtf8("farNearCmbBox"))
        self.farNearCmbBox.addItem(_fromUtf8(""))
        self.farNearCmbBox.addItem(_fromUtf8(""))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.FieldRole, self.farNearCmbBox)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(hwConfig_dialog)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_3)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.label_10 = QtGui.QLabel(self.groupBox_3)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_10)
        self.deflSignCmbBox = QtGui.QComboBox(self.groupBox_3)
        self.deflSignCmbBox.setObjectName(_fromUtf8("deflSignCmbBox"))
        self.deflSignCmbBox.addItem(_fromUtf8(""))
        self.deflSignCmbBox.addItem(_fromUtf8(""))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.deflSignCmbBox)
        self.label_11 = QtGui.QLabel(self.groupBox_3)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_11)
        self.sumThrNumDbl = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.sumThrNumDbl.setObjectName(_fromUtf8("sumThrNumDbl"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.sumThrNumDbl)
        self.label_12 = QtGui.QLabel(self.groupBox_3)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_12)
        self.label_13 = QtGui.QLabel(self.groupBox_3)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_13)
        self.iGainMaxNumDbl = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.iGainMaxNumDbl.setMaximum(100000.0)
        self.iGainMaxNumDbl.setObjectName(_fromUtf8("iGainMaxNumDbl"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.iGainMaxNumDbl)
        self.pGainMaxNumDbl = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.pGainMaxNumDbl.setMaximum(100000.0)
        self.pGainMaxNumDbl.setObjectName(_fromUtf8("pGainMaxNumDbl"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.FieldRole, self.pGainMaxNumDbl)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.saveNcancBtnBox = QtGui.QDialogButtonBox(hwConfig_dialog)
        self.saveNcancBtnBox.setOrientation(QtCore.Qt.Horizontal)
        self.saveNcancBtnBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.saveNcancBtnBox.setObjectName(_fromUtf8("saveNcancBtnBox"))
        self.verticalLayout.addWidget(self.saveNcancBtnBox)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 3)
        self.verticalLayout.setStretch(2, 3)
        self.verticalLayout.setStretch(3, 1)

        self.retranslateUi(hwConfig_dialog)
        QtCore.QObject.connect(self.saveNcancBtnBox, QtCore.SIGNAL(_fromUtf8("accepted()")), hwConfig_dialog.accept)
        QtCore.QObject.connect(self.saveNcancBtnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), hwConfig_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(hwConfig_dialog)

    def retranslateUi(self, hwConfig_dialog):
        hwConfig_dialog.setWindowTitle(_translate("hwConfig_dialog", "Hardware Config", None))
        self.groupBox.setTitle(_translate("hwConfig_dialog", "Connections", None))
        self.label.setText(_translate("hwConfig_dialog", "AFM IP", None))
        self.label_2.setText(_translate("hwConfig_dialog", "AFM Sub Port", None))
        self.label_14.setText(_translate("hwConfig_dialog", "AFM Pub Port", None))
        self.label_15.setText(_translate("hwConfig_dialog", "High res. device name", None))
        self.label_16.setText(_translate("hwConfig_dialog", "Monitor device name", None))
        self.label_3.setText(_translate("hwConfig_dialog", "Motors XY Port", None))
        self.label_4.setText(_translate("hwConfig_dialog", "Motors Z Port", None))
        self.groupBox_2.setTitle(_translate("hwConfig_dialog", "Piezo settings", None))
        self.label_5.setText(_translate("hwConfig_dialog", "Max Piezo voltage [V]", None))
        self.label_6.setText(_translate("hwConfig_dialog", "Min Piezo voltage [V]", None))
        self.label_7.setText(_translate("hwConfig_dialog", "Max Piezo ext [um]", None))
        self.label_8.setText(_translate("hwConfig_dialog", "Min Piezo ext [um]", None))
        self.label_9.setText(_translate("hwConfig_dialog", "Min piezo ext       =", None))
        self.farNearCmbBox.setItemText(0, _translate("hwConfig_dialog", "Far", None))
        self.farNearCmbBox.setItemText(1, _translate("hwConfig_dialog", "Near", None))
        self.groupBox_3.setTitle(_translate("hwConfig_dialog", "Other", None))
        self.label_10.setText(_translate("hwConfig_dialog", "Deflection sign", None))
        self.deflSignCmbBox.setItemText(0, _translate("hwConfig_dialog", "Signal increase = force increase", None))
        self.deflSignCmbBox.setItemText(1, _translate("hwConfig_dialog", "Signal increase = force decrease", None))
        self.label_11.setText(_translate("hwConfig_dialog", "Sum Threshold [V]", None))
        self.label_12.setText(_translate("hwConfig_dialog", "Integral Gain Max", None))
        self.label_13.setText(_translate("hwConfig_dialog", "Proportional Gain Max", None))

