from GUIs.hwConfig_dialog import *
from PyQt4.QtGui import QDialog,QMessageBox,QFileDialog
#from ConfigParser import ConfigParser
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
    
    
    def fillControls(self):
        
        self.afmIpLine.setText(self.parser.get('CONN', 'afmip'))
        self.afmSubPortNum.setValue(int(self.parser.get('CONN', 'afmsubport')))
        self.afmPubPortNum.setValue(int(self.parser.get('CONN', 'afmpubport')))
        self.deflNameLine.setText(self.parser.get('CONN', 'deflname'))
        self.torsNameLine.setText(self.parser.get('CONN', 'torsname'))
        self.sumNameLine.setText(self.parser.get('CONN', 'sumname'))
        self.zNameLine.setText(self.parser.get('CONN', 'zname')) 
        self.motorXyPortLine.setText(self.parser.get('CONN', 'xyport'))
        self.motorZPortLine.setText(self.parser.get('CONN', 'zport'))
        
        self.maxPiezoVoltNumDbl.setValue(float(self.parser.get('PIEZO', 'vmax')))
        self.minPiezoVoltNumDbl.setValue(float(self.parser.get('PIEZO', 'vmin')))
        self.maxPiezoExtNumDbl.setValue(float(self.parser.get('PIEZO', 'zmax')))
        self.minPiezoExtNumDbl.setValue(float(self.parser.get('PIEZO', 'zmin')))
        self.farNearCmbBox.setCurrentIndex(int(self.parser.get('PIEZO','nearfar')))
        
        self.deflSignCmbBox.setCurrentIndex(int(self.parser.get('OTHER','deflsign')))
        self.sumThrNumDbl.setValue(float(self.parser.get('OTHER', 'sumthr')))
        self.iGainMaxNumDbl.setValue(float(self.parser.get('OTHER', 'imax')))
        self.pGainMaxNumDbl.setValue(float(self.parser.get('OTHER', 'pmax')))
    
    
    def saveControls(self):
        
        self.parser.set('CONN', 'afmip',self.afmIpLine.text())
        self.parser.set('CONN', 'afmsumport',str(self.afmSubPortNum.value()))
        self.parser.set('CONN', 'afmpumport',str(self.afmPubPortNum.value()))
        self.parser.set('CONN', 'deflname',self.deflNameLine.text())
        self.parser.set('CONN', 'torsname',self.torsNameLine.text())
        self.parser.set('CONN', 'sumname',self.sumNameLine.text())
        self.parser.set('CONN', 'zname',self.zNameLine.text())
        self.parser.set('CONN', 'xyport',self.motorXyPortLine.text())
        self.parser.set('CONN', 'zport',self.motorZPortLine.text())
        
        self.parser.set('PIEZO', 'vmax',str(self.maxPiezoVoltNumDbl.value()))
        self.parser.set('PIEZO', 'vmin',str(self.minPiezoVoltNumDbl.value()))
        self.parser.set('PIEZO', 'zmax',str(self.maxPiezoExtNumDbl.value()))
        self.parser.set('PIEZO', 'zmin',str(self.minPiezoExtNumDbl.value()))
        self.parser.set('PIEZO','nearfar',str(self.farNearCmbBox.currentIndex()))
        
        self.parser.set('OTHER','deflsign',str(self.deflSignCmbBox.currentIndex()))
        self.parser.set('OTHER', 'sumthr',str(self.sumThrNumDbl.value()))
        self.parser.set('OTHER', 'imax',str(self.iGainMaxNumDbl.value()))
        self.parser.set('OTHER', 'pmax',str(self.pGainMaxNumDbl.value()))
        
        warningDial = QMessageBox(self)
        warningDial.setWindowTitle('Saving...')
        warningDial.setText('Do you want to create a new configuration file?')
        warningDial.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        warningDial.setDefaultButton(QMessageBox.No)
        answer = warningDial.exec_()
        if answer == 65536:
            fp = open(self.cfgFile,'w')
        else:
            fname = str(QFileDialog.getSaveFileName(self,'Choose a name for your new configuration file:',filter='Ini (*.ini)'))
            sf = splitext(fname)
            if sf[1] != '.ini':
                fname = sf[0]+'.ini'
            self.cfgFile = fname
            fp = open(fname,'w')
        
        self.parser.write(fp)
        fp.close()
    
    
    def accept(self):
        
        self.saveControls()
        super(hwConfig_dial,self).accept()   
        
        
        
        
         