from PyQt4.QtGui import QDialog

from GUIs.zPath_dialog import *


class zPath_dial(Ui_zPath_dialog,QDialog):
    
    def __init__(self,parent = None,segs = {},zStart = 0.0):
        
        super(zPath_dial,self).__init__(parent)
        
        self.setupUi(self)
        
        z,t = self.createTrack(segs,zStart)
        
        self.zPathPlot.plot(t,z,pen={'color':'g','width':2})
        
        
    def createTrack(self,segs,z0):
        
        zOld = z0
        tOld = 0.0
        
        zs = [z0]
        ts = [0.0]
        
        for s in segs:
            z = s['zLim']
            dz = abs(z-zOld)
            dt = s['holdT'] if s['direction'] == 2 else dz/s['speed']
            zs.append(z)
            ts.append(tOld+dt)
            tOld+=dt
            zOld = z
        
        return zs,ts