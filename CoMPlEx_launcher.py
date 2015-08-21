from PyQt4.QtGui import QMainWindow, QApplication

import sys

from GUIs.CoMPlEx_deriv import CoMPlEx_main

class MainW(QMainWindow,CoMPlEx_main):
    def __init__(self,parent = None):
        super(MainW,self).__init__(parent)
        self.setupUi(self)
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mainWin = MainW()
    mainWin.show()
    
    app.exec_()
    
