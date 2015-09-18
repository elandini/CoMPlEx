from PyQt4.QtGui import QApplication
import sys
from GUIs.CoMPlEx_deriv import CoMPlEx_main


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    mainWin = CoMPlEx_main()
    mainWin.show()
    
    app.exec_()
