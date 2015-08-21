from hwConfig_dialog import *
from PyQt4.QtGui import QDialog


class hwConfig_dial(Ui_hwConfig_dialog,QDialog):
    
    def __init__(self,parent = None):
        
        super(hwConfig_dial,self).__init__(parent)
        self.setupUi(self)
        self.setConnections()
        
        
    def setConnections(self):
        self.buttonBox.clicked.connect(self.close)