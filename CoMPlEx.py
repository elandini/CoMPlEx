try:
    from PyQt5.QtWidgets import QApplication
    ENV = 'PyQt5'
except:
    from PyQt4.QtGui import QApplication
    ENV = 'PyQt4'
import sys
from GUIs.CoMPlEx_Engine import CoMPlEx_main


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mainWin = CoMPlEx_main()
    mainWin.show()
    
    app.exec_()
