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

from GUIs.CoMPlEx_Engine import CoMPlEx_main

try:
    VERBOSE = sys.argv[1] == '-v' or sys.argv[1] == '--verbose'
except:
    VERBOSE = False

if __name__ == '__main__':
    
    if VERBOSE:
        print("Starting")
    app = QApplication(sys.argv)
    mainWin = CoMPlEx_main(verbose = VERBOSE)
    mainWin.show()
    
    app.exec_()
