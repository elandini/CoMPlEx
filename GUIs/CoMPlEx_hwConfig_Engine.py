import sys
CURRMOD = list(sys.modules.keys())
try:
    ENV = 'PyQt5'
    CURRMOD.index(ENV)
    from PyQt5.QtWidgets import QDialog,QMessageBox,QFileDialog
except:
    ENV = 'PyQt4'
    CURRMOD.index(ENV)
    from PyQt4.QtGui import QDialog,QMessageBox,QFileDialog

from GUIs.CoMPlEx_hwConfig_Dialog import Ui_hwConfig_dialog
# from ConfigParser import ConfigParser
from configparser import ConfigParser
from os.path import splitext


class hwConfig_dial(Ui_hwConfig_dialog,QDialog):
    
    def __init__(self,parent = None,cfgFile = None):
        
        self.parser = ConfigParser()
        super(hwConfig_dial,self).__init__(parent)
        self.setupUi(self)
        if cfgFile is None:
            self.cfgFile = 'config/defaultCfg.ini'
        else:
            self.cfgFile = cfgFile
        self.parser.read(self.cfgFile)
        self.fillControls()
        self.maxSpeedNumDbl.valueChanged.connect(self.toStartSpeedNumDbl.setMaximum)
    
    
    def fillControls(self):
        
        self.afmIpLine.setText(self.parser.get('CONN', 'afmip'))
        self.afmSubPortNum.setValue(int(self.parser.get('CONN', 'afmsubport')))
        self.afmPubPortNum.setValue(int(self.parser.get('CONN', 'afmpubport')))
        self.curveNameLine.setText(self.parser.get('CONN', 'curvename'))
        self.monitNameLine.setText(self.parser.get('CONN', 'monitname')) 
        self.xyCmdTagLine.setText(self.parser.get('CONN', 'xycmd'))
        self.xyResTagLine.setText(self.parser.get('CONN', 'xyres'))
        
        self.maxPiezoVoltNumDbl.setValue(float(self.parser.get('PIEZO', 'vmax')))
        self.minPiezoVoltNumDbl.setValue(float(self.parser.get('PIEZO', 'vmin')))
        self.maxPiezoExtNumDbl.setValue(float(self.parser.get('PIEZO', 'zmax')))
        self.minPiezoExtNumDbl.setValue(float(self.parser.get('PIEZO', 'zmin')))
        self.farNearCmbBox.setCurrentIndex(int(self.parser.get('PIEZO','nearfar')))
        self.maxSpeedNumDbl.setValue(float(self.parser.get('PIEZO','maxspeed')))
        self.toStartSpeedNumDbl.setValue(float(self.parser.get('PIEZO','tostartspeed')))
        
        self.deflSignCmbBox.setCurrentIndex(int(self.parser.get('OTHER','deflsign')))
        self.maxDeflVoltNumDbl.setValue(float(self.parser.get('OTHER','dvmax')))
        self.minDeflVoltNumDbl.setValue(float(self.parser.get('OTHER','dvmin')))
        self.sumThrNumDbl.setValue(float(self.parser.get('OTHER', 'sumthr')))
        self.iGainMaxNumDbl.setValue(float(self.parser.get('OTHER', 'imax')))
        self.pGainMaxNumDbl.setValue(float(self.parser.get('OTHER', 'pmax')))
        self.defDirLine.setText(self.parser.get('OTHER', 'defdir'))
        self.defBaseNameLine.setText(self.parser.get('OTHER', 'defbasename'))
    
    
    def saveControls(self):
        
        self.parser.set('CONN', 'afmip',self.afmIpLine.text())
        self.parser.set('CONN', 'afmsubport',str(self.afmSubPortNum.value()))
        self.parser.set('CONN', 'afmpubport',str(self.afmPubPortNum.value()))
        self.parser.set('CONN', 'curvename',self.curveNameLine.text())
        self.parser.set('CONN', 'monitname',self.monitNameLine.text())
        self.parser.set('CONN', 'xycmd',self.xyCmdTagLine.text())
        self.parser.set('CONN', 'xyres',self.xyResTagLine.text())
        
        self.parser.set('PIEZO', 'vmax',str(self.maxPiezoVoltNumDbl.value()))
        self.parser.set('PIEZO', 'vmin',str(self.minPiezoVoltNumDbl.value()))
        self.parser.set('PIEZO', 'zmax',str(self.maxPiezoExtNumDbl.value()))
        self.parser.set('PIEZO', 'zmin',str(self.minPiezoExtNumDbl.value()))
        self.parser.set('PIEZO','nearfar',str(self.farNearCmbBox.currentIndex()))
        self.parser.set('PIEZO', 'maxspeed',str(self.maxSpeedNumDbl.value()))
        self.parser.set('PIEZO', 'tostartspeed',str(self.toStartSpeedNumDbl.value()))
        
        self.parser.set('OTHER','deflsign',str(self.deflSignCmbBox.currentIndex()))
        self.parser.set('OTHER','dvmax',str(self.maxDeflVoltNumDbl.value()))
        self.parser.set('OTHER','dvmin',str(self.minDeflVoltNumDbl.value()))
        self.parser.set('OTHER', 'sumthr',str(self.sumThrNumDbl.value()))
        self.parser.set('OTHER', 'imax',str(self.iGainMaxNumDbl.value()))
        self.parser.set('OTHER', 'pmax',str(self.pGainMaxNumDbl.value()))
        self.parser.set('OTHER', 'defdir', self.defDirLine.text())
        self.parser.set('OTHER', 'defbasename', self.defBaseNameLine.text())
        
        warningDial = QMessageBox(self)
        warningDial.setWindowTitle('Saving...')
        warningDial.setText('Do you want to create a new configuration file?')
        warningDial.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        warningDial.setDefaultButton(QMessageBox.No)
        answer = warningDial.exec_()
        if answer == 65536:
            fp = open(self.cfgFile,'w')
        else:
            if ENV == 'PyQt5':
                fname = str(QFileDialog.getSaveFileName(self,'Choose a name for your new configuration file:',filter='Ini (*.ini)')[0])
            else:
                fname = str(QFileDialog.getSaveFileName(self,'Choose a name for your new configuration file:',filter='Ini (*.ini)'))
            sf = splitext(fname)
            if sf[1] != '.ini':
                fname = sf[0]+'.ini'
            fp = open(fname,'w')
        
        self.parser.write(fp)
        fp.close()
    
    
    def accept(self):
        
        self.saveControls()
        warningDial = QMessageBox(self)
        warningDial.setWindowTitle('WARNING')
        warningDial.setText('The changes made to the configuration file will become effective the next time you open CoMPlEx ui')
        warningDial.setStandardButtons(QMessageBox.Ok)
        answer = warningDial.exec_()
        super(hwConfig_dial,self).accept()   
        
        
        
        
         