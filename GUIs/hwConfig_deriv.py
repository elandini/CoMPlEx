from hwConfig_dialog import *
from PyQt4.QtGui import QDialog
from ConfigParser import ConfigParser


class hwConfig_dial(Ui_hwConfig_dialog,QDialog):
    
    def __init__(self,parent = None,cfgFile = None):
        
        self.parser = ConfigParser()
        super(hwConfig_dial,self).__init__(parent)
        self.setupUi(self)
        if cfgFile is None:
            self.cfgFile = 'defaultCfg.ini'
        else:
            self.cfgFile = cfgFile
        self.parser.read(self.cfgFile)
        self.fillControls()
    
    
    def fillControls(self):
        
        self.afmIpLine.setText(self.parser.get('CONN', 'afmip'))
        self.afmPortNum.setValue(int(self.parser.get('CONN', 'afmport')))
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
        self.parser.set('CONN', 'afmport',str(self.afmPortNum.value()))
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
        
        fp = open(self.cfgFile,'w')
        
        self.parser.write(fp)
    
    
    def accept(self):
        
        self.saveControls()
        super(hwConfig_dial,self).accept()    