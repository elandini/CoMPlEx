from GUIs.CoMPlEx_zPath_Dialog import *
import sys
CURRMOD = list(sys.modules.keys())
try:
    ENV = 'PyQt5'
    CURRMOD.index(ENV)
    from PyQt5.QtWidgets import QApplication
except:
    ENV = 'PyQt4'
    CURRMOD.index(ENV)
    from PyQt4.QtGui import QApplication

import sys
from GUIs.CoMPlEx_Engine import CoMPlEx_main


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mainWin = CoMPlEx_main()
    mainWin.show()
    
    app.exec_()
