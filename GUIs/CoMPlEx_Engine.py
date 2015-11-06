import sys
CURRMOD = list(sys.modules.keys())
try:
    ENV = 'PyQt5'
    CURRMOD.index(ENV)
    from PyQt5.QtWidgets import QFileDialog, QMainWindow, QSpinBox
    from PyQt5.QtWidgets import QDoubleSpinBox, QMessageBox, QCheckBox, QLineEdit
    from PyQt5.QtGui import QIcon, QPixmap, QColor
    from PyQt5.QtCore import QThread
    from PyQt5 import QtCore
    import pyqtgraph as pg

except:
    ENV = 'PyQt4'
    CURRMOD.index(ENV)
    from PyQt4.QtGui import QFileDialog, QMainWindow,QIcon, QPixmap, QColor
    from PyQt4.QtGui import QSpinBox, QDoubleSpinBox, QMessageBox, QCheckBox, QLineEdit
    from PyQt4.QtCore import QThread
    from PyQt4 import QtCore
    import pyqtgraph as pg

from GUIs.CoMPlEx_MainGUI import Ui_CoMPlEx_GUI
from GUIs.CoMPlEx_hwConfig_Engine import hwConfig_dial
from GUIs.CoMPlEx_zPath_Engine import zPath_dial

from os import makedirs
from subprocess import Popen
from os.path import splitext, split, join, exists
from configparser import ConfigParser
import numpy as np
from scipy.signal import hilbert
from time import sleep

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
try:
    import epz as tempEpz
    import inspect
    _,_,keys,_ = inspect.getargspec(tempEpz.CMD.__init__())
    if 'tag' not in keys:
        from libs.epz import epz as tempEpz
    epz = tempEpz
except:
    from libs.epz import epz

from libs.curveLib import curve,segment
from libs.complex2epz import Interpreter

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


CHUNK = 1000
DEC = 10
NOTLEN = 50

'''
1 #0033CC
2 #FF0000
3 #009900
4 #9933FF
5 #996600
6 #660033
7 #000000
8 #8D9494

'''


class CoMPlEx_main(QMainWindow,Ui_CoMPlEx_GUI):
    
    channels = ['Engage','Calib QPD','Calib K','FvsD curve','FvsD map','Custom curve','Custom map']
    pens = [{'color':'#0033CC','width':1},{'color':'#FF0000','width':1},{'color':'#009900','width':1},
            {'color':'#9933FF','width':1},{'color':'#996600','width':1},{'color':'#660033','width':1},
            {'color':'#000000','width':1},{'color':'#8D9494','width':1}]
    ramblingPen = {'color':'#0033CC','width':2}
    
    def __init__(self,parent = None):
    
        super(CoMPlEx_main,self).__init__(parent)
        self.setupUi(self)
        
        icon = QIcon()
        icon.addPixmap(QPixmap(_fromUtf8("GUIs/Icons/altZ.bmp")), QIcon.Normal, QIcon.Off)
        self.altZSegBtn.setIcon(icon)
        
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(_fromUtf8("GUIs/Icons/altF.bmp")), QIcon.Normal, QIcon.Off)
        self.altFSegBtn.setIcon(icon1)
        
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(_fromUtf8("GUIs/Icons/far.bmp")), QIcon.Normal, QIcon.Off)
        self.farSegBtn.setIcon(icon2)
        
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(_fromUtf8("GUIs/Icons/near.bmp")), QIcon.Normal, QIcon.Off)
        self.nearSegBtn.setIcon(icon3)
        
        self.actionNdockDict = {self.action_Motors:[self.motorsDock,'isChecked','setVisible','visibilityChanged'],
                                self.action_Settings:[self.settingsDock,'isChecked','setVisible','visibilityChanged'],
                                self.action_Remote:[self.remoteDock,'isChecked','setVisible','visibilityChanged'],
                                self.action_QPD_and_piezo:[self.qpdNpiezoDock,'isChecked','setVisible','visibilityChanged'],
                                self.motorsDock:[self.action_Motors,'isVisible','setChecked','changed'],
                                self.settingsDock:[self.action_Settings,'isVisible','setChecked','changed'],
                                self.remoteDock:[self.action_Remote,'isVisible','setChecked','changed'],
                                self.qpdNpiezoDock:[self.action_QPD_and_piezo,'isVisible','setChecked','changed']}

        self.custFvsdSegs = []
        self.zTrigBase = 0.0
        self.fTrigBase = 0.0
        self.nonCntF = 0.0
        
        self.programs = {'Engage':self.remoteEngage,'Calib QPD':self.remoteCalibQPD,'Calib K':self.calibK,
                         'FvsD curve':self.fvsd,'FvsD map':self.fvsdMap,'Custom curve':self.custom,'Custom map':self.customMap}

        if ENV == 'PyQt5':
            self.cfgFile = str(QFileDialog.getOpenFileName(self,'Select a configuration file',filter='Ini (*.ini)')[0])
        else:
            self.cfgFile = str(QFileDialog.getOpenFileName(self,'Select a configuration file',filter='Ini (*.ini)'))
        if self.cfgFile == '':
            self.cfgFile = 'config/defaultCfg.ini'
        self.channelCmbBox.clear()
        self.channelMng('Engage')
        self.laserSpot = self.alignPlot.plot([0],[0],pen = None, symbol = 'o', symbolPen = 'r', symbolSize = 50, symbolBrush = QColor(0,0,0,128))
        self.alignPlot.plot([0],[0],pen = None, symbol = 'o', symbolPen = {'color':'b','width':2}, symbolSize = 50, symbolBrush = QColor(255,255,255,0))
        self.alignPlot.plotItem.showAxis('top',True)
        self.alignPlot.plotItem.showAxis('right',True)
        self.alignPlot.plotItem.showGrid(True,True,1)
        self.alignPlot.plotItem.setRange(xRange = [-10,10],yRange = [-10,10])
        self.alignPlot.plotItem.setMouseEnabled(False,False)
        
        self.complexEnv = epz.Environment()
    
        self.currentCurve = None
        self.currentCurveNum = 0
        self.currentPtNum = 0
        self.saveMe = False
        
        self.expInProgress = False
        self.engaging = False
        self.engaged = False

        self.speedGroups = {self.appSpeedNumDbl:[True,self.startZNumDbl,self.endZNumDbl],
                            self.retrSpeedNumDbl:[True,self.startZNumDbl,self.endZNumDbl],
                            self.speedcNumDbl:[True,self.endZcNumDbl,None],
                            self.startZNumDbl:[False,self.startZNumDbl,self.endZNumDbl,self.appSpeedNumDbl,self.retrSpeedNumDbl],
                            self.endZNumDbl:[False,self.startZNumDbl,self.endZNumDbl,self.appSpeedNumDbl,self.retrSpeedNumDbl],
                            self.endZcNumDbl:[False,self.endZcNumDbl,False,self.speedcNumDbl]}

        self.applyConfig()
        self.epzConnect()
        self.epzConnections()
        self.actionNdocksConnections()
        self.buttonsConnections()
        self.genericConnetions()
        self.startEpzs()
    
    
    def channelMng(self,channel,operation = '+'):
        
        if operation == '+':
            if channel in self.channels:
                self.channelCmbBox.addItem(channel)
                del self.channels[self.channels.index(channel)]
        elif operation == '-':
            if channel not in self.channels:
                self.channelCmbBox.removeItem(self.channelCmbBox.findText(channel))
                self.channels.append(channel)

    
    def applyConfig(self):
        
        try:
            if self.cfgFile != self.hwDial.cfgFile:
                self.cfgFile = self.hwDial.cfgFile
        except:
            pass
        
        parser = ConfigParser()
        parser.read(self.cfgFile)

        self.privates = {}
        for  o in parser.options('PRIVATE'):
            self.privates[o] = parser.get('PRIVATE',o)

        self.sumThr = float(parser.get('OTHER','sumthr'))
        self.deflSign = (-1)**(int(parser.get('OTHER','deflsign')))
        self.iGainNumDbl.setMaximum(float(parser.get('OTHER','imax')))
        self.pGainNumDbl.setMaximum(float(parser.get('OTHER','pmax')))
        self.baseCurveName = parser.get('OTHER','defbasename')
        self.curveDir = parser.get('OTHER','defdir')
        
        self.forwarderIP = parser.get('CONN','afmip')
        self.forwarderPubPort = parser.get('CONN','afmpubport')
        self.forwarderSubPort = parser.get('CONN','afmsubport')
        self.curveName = parser.get('CONN','curvename')
        self.monitName = parser.get('CONN','monitname')
        self.xyCmdTag = parser.get('CONN','xycmd')
        self.xyResTag = parser.get('CONN','xyres')
        
        self.complexEnv.pubport = self.forwarderPubPort
        self.complexEnv.subport = self.forwarderSubPort
        self.complexEnv.device = self.curveName
        self.complexEnv.epserver = self.forwarderIP
        
        zM = float(parser.get('PIEZO','zmax'))*1000
        zm = float(parser.get('PIEZO','zmin'))*1000
        
        zvM = float(parser.get('PIEZO','vmax'))
        zvm = float(parser.get('PIEZO','vmin'))
        
        self.zVtoNm = lambda x: ((x-zvm)/(zvM-zvm)*(zM-zm)+zm)
        self.zNmtoV = lambda x: ((x-zm)/(zM-zm)*(zvM-zvm)+zvm)
        self.zNmtoVRel = lambda x: (x/(zM-zm)*(zvM-zvm))
        self.zVtoNmRel = lambda x: (x/(zvM-zvm)*(zM-zm))
        
        self.toStartSpeed = float(parser.get('PIEZO','tostartspeed'))
        
        self.endZNumDbl.setMaximum(zM)
        self.endZcNumDbl.setMaximum(zM)
        self.endZNumDbl.setMinimum(zm)
        self.endZcNumDbl.setMinimum(zm)
        self.startZNumDbl.setMaximum(zM)
        self.startZcNumDbl.setMaximum(zM)
        self.startZNumDbl.setMinimum(zm)
        self.startZcNumDbl.setMinimum(zm)
        self.calibStimZOffsetNumDbl.setMaximum(zM)
        self.calibStimZOffsetNumDbl.setMinimum(zm)
        self.zPiezoNumDbl.setMinimum(zm/1000.0)
        self.zPiezoNumDbl.setMaximum(zM/1000.0)
        self.zPiezoProg.setMinimum(zm/1000.0)
        self.zPiezoProg.setMaximum(zM/1000.0)
        self.nearFar = (-1)**(int(parser.get('PIEZO','nearfar')=='0'))
        self.zPiezoProg.setInvertedAppearance(self.nearFar<0)
        maxV = float(parser.get('PIEZO','maxspeed'))
        self.appSpeedNumDbl.setMaximum(maxV)
        self.retrSpeedNumDbl.setMaximum(maxV)
        self.speedcNumDbl.setMaximum(maxV)

        self.deflVmax = float(parser.get('OTHER','dvmax'))
        self.deflVmin = float(parser.get('OTHER','dvmin'))
        self.maxFNumDbl.setMaximum(self.deflVmax)
        self.maxFNumDbl.setMinimum(0)
        self.setPtNumDbl.setMaximum(self.deflVmax)
        self.setPtNumDbl.setMinimum(self.deflVmin)
        self.endFcNumDbl.setMaximum(self.deflVmax)
        self.endFcNumDbl.setMinimum(0)

        self.systemDict = {'zMaxNm':zM,
                           'zMinNm':zm,
                           'zMaxV':zvM,
                           'zMinV':zvm}

        self.deflectionToV = self.deflSign/(self.kNumDbl.value()*self.kdNumDbl.value())

        self.simplePath = parser.get('SIMPLE','path')
        self.action_Open_SiMPlE.setEnabled(len(self.simplePath) > 2)

        
    def epzConnect(self):
        
        self.curveData = epz.QtDATA(self.complexEnv)
        self.monitData = epz.QtDATA(self.complexEnv,device=self.monitName,tag='DATA')

        self.curveIntpr = Interpreter(self.complexEnv)
        self.monitIntpr = Interpreter(self.complexEnv,self.monitName)
        
        self.xyCmd = epz.CMD(self.complexEnv,self.monitName,self.xyCmdTag)
        
        self.xyRes = epz.QtCMDREC(self.complexEnv,self.monitName,self.xyResTag)
        
        self.curveData.notify = True
        self.curveData.save = False
        self.monitData.notify = True
        self.monitData.save = False
        
        self.curveData.chunk = CHUNK
        self.curveData.decimate = DEC
        self.monitData.chunk = CHUNK
        self.monitData.decimate = DEC
        self.monitData.notifyLength = NOTLEN


    def startEpzs(self):

        sleep(0.5)
        self.curveData.start()
        self.monitData.start()
        self.curveIntpr.startDev()
        self.monitIntpr.startDev()
        self.xyRes.start()

#### Parameters management #############################################################################################

    def getParamsDict(self):

        baseDict = {QSpinBox:['NUM','.value()','.setValue(',[]],QDoubleSpinBox:['DBL','.value()','.setValue(',[]],
                    QLineEdit:['LINE','.text()','.setText(',[]],QCheckBox:['CKBOX','.isChecked()','.setChecked(',[]]}

        for d in dir(self):
            dObj = getattr(self, d)
            try:
                if dObj.isReadOnly():
                    continue
            except:
                pass
            if type(dObj) in baseDict.keys():
                baseDict[type(dObj)][3].append(d)
            else:
                pass

        return baseDict

    
    def saveParams(self):

        if ENV == 'PyQt5':
            parFileName = str(QFileDialog.getSaveFileName(self,'Choose a name for you parameters file',filter='Parameters Files (*.par)')[0])
        else:
            parFileName = str(QFileDialog.getSaveFileName(self,'Choose a name for you parameters file',filter='Parameters Files (*.par)'))
        if parFileName == '':
            return None
        splitName = splitext(parFileName)
        if splitName[1] != '.par':
            parFileName = splitName[0]+'.par'
        
        sDict = self.getParamsDict()
        paramsFile = open(parFileName,'w')
        paramsParser = ConfigParser()
        
        paramsParser.add_section('MISC')
        paramsParser.set('MISC','afm',self.cfgFile)
        for k in sDict.keys():
            paramsParser.add_section(sDict[k][0])
            for i in range(len(sDict[k][3])):
                paramsParser.set(sDict[k][0], sDict[k][3][i], str(eval('self.'+sDict[k][3][i]+sDict[k][1])))
        
        paramsParser.write(paramsFile)
        paramsFile.close()
        
    
    def loadParams(self):
        
        if ENV == 'PyQt5':
            parFileName = str(QFileDialog.getOpenFileName(self,'Choose a parameter file:',filter='Par (*.par)')[0])
        else:
            parFileName = str(QFileDialog.getOpenFileName(self,'Choose a parameter file:',filter='Par (*.par)'))
        if parFileName == '':
            return None
        lDict = self.getParamsDict()
        #paramsFile = open(parFileName,'r')
        paramsParser = ConfigParser()
        paramsParser.read(parFileName)
        if paramsParser.get('MISC', 'afm') != self.cfgFile:
            warning = QMessageBox(self)
            warning.setText('You tried to load parameters that have been saved for another AFM\n'+
                            'Please choose a parameter file for you current AFM')
            warning.exec_()
            self.loadParams()
        attrList = dir(self)
        for a in attrList:
            for k in lDict.keys():
                if a in lDict[k][3]:
                    value = paramsParser.get(lDict[k][0],a.lower())
                    try:
                        value = str(eval(value))
                    except:
                        value = '\'' + value + '\''
                    eval('self.' + a + lDict[k][2] + value + ')')

########################################################################################################################

#### Parameters management #############################################################################################

    def uploadEpzParam(self):
        
        culprit = self.sender()

        if culprit is self.uploadPGainBtn:
            self.curveIntpr.setP(self.pGainNumDbl.value())
        elif culprit is self.uploadIGainBtn:
            self.curveIntpr.setI(self.iGainNumDbl.value())
        elif culprit is self.uploadSetPtBtn:
            self.curveIntpr.setSetPoint(self.setPtNumDbl.value()*self.deflectionToV)
        elif culprit is self.uploadFbBtn:
            self.curveIntpr.setP(self.pGainNumDbl.value())
            self.curveIntpr.setI(self.iGainNumDbl.value())
            self.curveIntpr.setSetPoint(self.setPtNumDbl.value()*self.deflectionToV)
        
        
    def changeRefDefl(self):
        
        self.maxFNumDbl.setMaximum(self.deflVmax*self.kdNumDbl.value()*self.kNumDbl.value())
        self.maxFNumDbl.setMinimum(0)
        self.setPtNumDbl.setMaximum(self.deflVmax*self.kdNumDbl.value()*self.kNumDbl.value())
        self.setPtNumDbl.setMinimum(self.deflVmin*self.kdNumDbl.value()*self.kNumDbl.value())
        self.endFcNumDbl.setMaximum(self.deflVmax*self.kdNumDbl.value()*self.kNumDbl.value())
        self.endFcNumDbl.setMinimum(0)
        
        self.label_7.setText('Set Point[V]' if self.kdNumDbl.value() == 1 else ('Set Point[nm]' if self.kNumDbl.value() == 1 else 'Set Point[pN]'))

        self.deflectionToV = self.deflSign/(self.kNumDbl.value()*self.kdNumDbl.value())

        if self.kdNumDbl.value() != 1 and self.kNumDbl.value() != 1 and self.engaged:
            self.channelMng('FvsD curve')
            self.channelMng('FvsD curve')
            self.channelMng('FvsD map')
            self.channelMng('Custom curve')
            self.channelMng('Custom map')
        
        
    def dockMng(self):
        
        culprit = self.sender()
        other = self.actionNdockDict[culprit][0]
        functions = self.actionNdockDict[culprit][1:]
        
        eval('other.'+functions[2]+'.disconnect()')
        
        check = eval('culprit.'+functions[0])
        set = eval('other.'+functions[1])
        
        set(check())
        
        eval('other.'+functions[2]+'.connect(self.dockMng)')
        
        
    def showDial(self):
        
        culprit = self.sender()
        
        if culprit is self.action_Edit_config:
            self.hwDial = hwConfig_dial(self,self.cfgFile)
            self.hwDial.exec_()
        elif culprit is self.showZTravelBtn:
            self.plotSeg()
    
    
    def getDataDir(self):
        
        dir = QFileDialog.getExistingDirectory(self, 'Select a directory...\n')
        self.dirLine.setText(dir)
    
    
    def zMonitProg(self):
        
        culprit = self.sender()
        newVal = culprit.value()
        
        self.zPiezoProg.setValue(newVal)
        
        
    def qpdMonitProgs(self):
        
        culprit = self.sender()
        newVal = culprit.value()
        
        if culprit == self.deflNumDbl:
            if newVal < 0:
                self.deflNegProg.setValue(abs(newVal))
                self.deflPosProg.setValue(0)
            elif newVal > 0:
                self.deflPosProg.setValue(newVal)
                self.deflNegProg.setValue(0)
            else:
                self.deflNegProg.setValue(0)
                self.deflPosProg.setValue(0)
            self.laserSpot.setData(self.laserSpot.xData,[newVal])
        elif culprit == self.torsNumDbl:
            if newVal < 0:
                self.torsNegProg.setValue(abs(newVal))
                self.torsPosProg.setValue(0)
            elif newVal > 0:
                self.torsPosProg.setValue(newVal)
                self.torsNegProg.setValue(0)
            else:
                self.torsNegProg.setValue(0)
                self.torsPosProg.setValue(0)
            self.laserSpot.setData([newVal],self.laserSpot.yData)
        else:
            self.sumProg.setValue(newVal)
            self.laserSpot.setSymbolBrush(QColor(int(25.5*newVal),0,0,128))


    def sendZ(self,v):

        #z = np.array(v[1])
        #zValue = self.zVtoNm(np.mean(z))/1000.0
        zValue = self.zVtoNm(v)/1000.0
        self.zPiezoNumDbl.setValue(zValue)
        
        
    def startAnalyzing(self):
        
        p = Popen('python3 '+self.simplePath)
    
    
    def getStandardSeg(self):
        
        stdSegments = []
        types = ['Zconst','Fconst','Vconst','Vconst']
        seg = {}

        seg['zLim'] = abs(self.endZNumDbl.value()-self.startZNumDbl.value())
        seg['fLim'] = self.maxFNumDbl.value()
        seg['speed'] = self.appSpeedNumDbl.value()
        seg['direction'] = 3
        seg['type'] = types[seg['direction']]
        seg['holdT'] = 0
        
        stdSegments.append(seg)
        
        if self.holdTimeNumDbl.value()>0:
            seg = {}
            seg['zLim'] = 0
            seg['fLim'] = 0
            seg['speed'] = 0
            seg['direction'] = 1 if self.constForceCkBox.isChecked() else 0
            seg['type'] = types[seg['direction']] 
            seg['holdT'] = self.holdTimeNumDbl.value()
        
            stdSegments.append(seg)
        
        seg = {}
        
        seg['zLim'] = abs(self.startZNumDbl.value()-self.endZNumDbl.value())
        seg['fLim'] = self.maxFNumDbl.minimum()
        seg['speed'] = self.retrSpeedNumDbl.value()
        seg['direction'] = 2
        seg['type'] = types[seg['direction']]
        seg['holdT'] = 0
        
        stdSegments.append(seg)
        
        return stdSegments
        
        
    def addSeg(self):
        
        seg = {}
        types = ['Zconst','Fconst','Vconst','Vconst']
        
        seg['zLim'] = self.endZcNumDbl.value()
        seg['fLim'] = self.endFcNumDbl.value()
        seg['speed'] = self.speedcNumDbl.value()
        seg['direction'] = self.getDir()
        seg['type'] = types[seg['direction']]
        seg['holdT'] = self.holdTimecNumDbl.value()
        
        self.custFvsdSegs.append(seg)
        
        self.segCmbBox.addItem('Segment: ' + str(self.segCmbBox.count()))
        
        if not self.removeSegBtn.isEnabled():
            self.removeSegBtn.setEnabled(True)
            self.updateSegBtn.setEnabled(True)
        self.segCmbBox.setCurrentIndex(self.segCmbBox.count()-1)
        
        
    def removeSeg(self):
        
        junkInd = self.segCmbBox.currentIndex()
        for i in range(self.segCmbBox.count()-(junkInd+1)):
            num = i+junkInd
            self.segCmbBox.setItemText(i+junkInd+1,'Segment: '+str(num))
        self.segCmbBox.removeItem(junkInd)
        del self.custFvsdSegs[junkInd]
        self.removeSegBtn.setEnabled(len(self.custFvsdSegs))
        self.updateSegBtn.setEnabled(len(self.custFvsdSegs))
        if len(self.custFvsdSegs):
            self.segCmbBox.setCurrentIndex(0)
        else:
            self.showSeg()
        
        
    def setDir(self,ind):
        
        directioners = [self.altZSegBtn,self.altFSegBtn,self.farSegBtn,self.nearSegBtn]
        
        i = 0
        for d in directioners:
            d.setEnabled(ind != i)
            i+=1
        
        
    def getDir(self):
        
        direction = (not self.altZSegBtn.isEnabled())*0 + (not self.altFSegBtn.isEnabled())*1 + (not self.farSegBtn.isEnabled())*2 + (not self.nearSegBtn.isEnabled())*3
        return direction
        
        
    def changeDir(self):
        
        culprit = self.sender()
        directioners = [self.altZSegBtn,self.altFSegBtn,self.farSegBtn,self.nearSegBtn]
        
        direction = directioners.index(culprit)
        del directioners[direction]
        
        culprit.setEnabled(False)
        
        for d in directioners:
            d.setEnabled(True)
        
        if direction>1:
            self.holdTimecNumDbl.setValue(0)
            self.holdTimecNumDbl.setEnabled(False)
            self.endZcNumDbl.setEnabled(True)
            self.endFcNumDbl.setEnabled(True)
            self.speedcNumDbl.setEnabled(True)
        else:
            self.endZcNumDbl.setValue(0)
            self.endFcNumDbl.setValue(0)
            self.speedcNumDbl.setValue(0)
            self.endZcNumDbl.setEnabled(False)
            self.endFcNumDbl.setEnabled(False)
            self.speedcNumDbl.setEnabled(False)
            self.holdTimecNumDbl.setEnabled(True)
        
        
    def showSeg(self):
        
        directioners = [self.altZSegBtn,self.altFSegBtn,self.farSegBtn,self.nearSegBtn]
        
        if self.segCmbBox.count()==0:
            self.endZcNumDbl.setValue(0)
            self.endFcNumDbl.setValue(0)
            self.speedcNumDbl.setValue(0)
            self.holdTimecNumDbl.setValue(0)
            
            self.endZcNumDbl.setEnabled(True)
            self.endFcNumDbl.setEnabled(True)
            self.speedcNumDbl.setEnabled(True)
            self.holdTimecNumDbl.setEnabled(True)
            
            for d in directioners:
                d.setEnabled(True)
            
            return None
        
        seg = self.custFvsdSegs[self.segCmbBox.currentIndex()]
        self.endZcNumDbl.setValue(seg['zLim'])
        self.endFcNumDbl.setValue(seg['fLim'])
        self.speedcNumDbl.setValue(seg['speed'])
        self.holdTimecNumDbl.setValue(seg['holdT'])
        self.setDir(seg['direction'])
        
        
    def updateSeg(self):
        
        ind = self.segCmbBox.currentIndex()
        types = ['Zconst','Fconst','Vconst','Vconst']
        
        self.custFvsdSegs[ind]['zLim'] = self.endZcNumDbl.value()
        self.custFvsdSegs[ind]['fLim'] = self.endFcNumDbl.value()
        self.custFvsdSegs[ind]['speed'] = self.speedcNumDbl.value()
        self.custFvsdSegs[ind]['direction'] = self.getDir()
        self.custFvsdSegs[ind]['type'] = types[self.custFvsdSegs[ind]['direction']]
        self.custFvsdSegs[ind]['holdT'] = self.holdTimecNumDbl.value()
        self.custFvsdSegs[ind]['fbOn'] = self.altFSegBtn.isChecked()
            
            
    def plotSeg(self):
        
        zPathDial = zPath_dial(self,self.custFvsdSegs,self.startZcNumDbl.value())
        zPathDial.exec_()
        
        
    def remotePlay(self):
        
        channel = self.channelCmbBox.currentText()
        
        self.programs[channel]()
        
        self.channelCmbBox.setEnabled(False)
        self.playBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        
        
    def remoteStop(self):
        
        channel = self.channelCmbBox.currentText()
        self.channelCmbBox.setEnabled(True)
        self.playBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        try:
            self.curveData.chunkReceived.disconnect()
        except:
            pass
        if channel == 'Calib QPD' or channel == 'Calib K':
            self.goToRest()
        elif channel == 'Engage':
            self.goToRest()
        else:
            self.stopExperiment()
    
    
    def motorRemoteCmd(self):
        
        culprit = self.sender()
        
        cmdDict = {self.xPlusBtn: ['M',[self.xStepNumNum.value(),0]],
                    self.xMinusBtn: ['M',[-1*self.xStepNumNum.value(),0]],
                    self.yPlusBtn: ['M',[0,self.yStepNumNum.value()]],
                    self.yMinusBtn: ['M',[0,-1*self.yStepNumNum.value()]],
                    self.goCenterBtn: ['GZ',[]],
                    self.resetXYBtn: ['SZ',[]]}
        self.xyCmd.send(cmdDict[culprit][0],cmdDict[culprit][1])
        
        
    def makeAstep(self,step1,step2):
        
        self.xyCmd.send('M',[step1,step2])
    
    
    def remoteEngage(self):

        self.rdsLine.setText('Engaging...')

        self.channelMng('FvsD curve')
        self.channelMng('FvsD map')
        self.channelMng('Custom curve')
        self.channelMng('Custom map')

        '''
        self.curveIntpr.setP(self.pGainNumDbl.value())
        self.curveIntpr.setI(self.iGainNumDbl.value())
        self.curveIntpr.setSetPoint(self.setPtNumDbl.value()*self.deflectionToV)

        self.ramblingPlot = self.centralPlot.plot([],[],pen = self.ramblingPen)

        self.curveIntpr.setTriggersSwitch(0,0,0)
        self.curveIntpr.feedbackOn()
        self.engaging = True
        self.curveData.chunkReceived.connect(self.engage)
        '''


    def engage(self,v):

        pass

        '''
        self.ramblingPlotManager(v)
        if np.mean(np.array(v[2])/self.deflectionToV)>=self.setPtNumDbl.value():
            self.engaged = True
            self.rdsLine.setText('Engaged')
            self.channelMng('Calib QPD')
            self.channelMng('Calib K')
        else:
            self.engaged = False
            self.rdsLine.setText('Engaging...')
            self.channelMng('Calib QPD','-')
            self.channelMng('Calib K','-')

        '''

        
    def remoteCalibQPD(self):
        
        self.channelMng('Calib K')
        self.rdsLine.setText('QPD calibration')
        self.curveIntpr.setSine()
        self.curveData.stateChanged.connect(self.calibQPD)


    def calibQPD(self):

        tempQueue = self.curveData.queue[0]
        zStim,fRes = self.emptyDataQueue(tempQueue)
        dRes = fRes/(self.kNumDbl.value()*self.kdNumDbl.value())

        dRes -= np.mean(dRes)
        zStim -= np.mean(zStim)

        shiftedStim = -1*(hilbert(zStim)).imag
        ampl = (np.max(zStim)-np.min(zStim))/2

        re = np.multiply(dRes,shiftedStim)*2/(ampl**2)
        im = np.multiply(dRes,zStim)*2/(ampl**2)

        kd = abs(np.mean(re)+1j*np.mean(im))

        self.kdNumDbl.setValue(kd)

        del self.curveData.queue[0]
        
        
    def calibK(self):
        
        self.channelMng('FvsD curve')
        self.channelMng('FvsD map')
        self.channelMng('Custom curve')
        self.channelMng('Custom map')
        self.rdsLine.setText('Elastic constant calibration')


    # Curve management functions


    def manageSpeedUpdate(self):

        culprit = self.sender()

        speedOrNot = self.speedGroups[culprit][0]

        za = self.speedGroups[culprit][1].value()
        try:
            zb = self.speedGroups[culprit][2].value()
        except:
            zb = 0.0

        if speedOrNot:
            speed = culprit.value()
            stopMe = (za == 0 and zb == 0) or speed == 0
            if stopMe:
                return None
            rs,t6t = self.speedToDacStep(speed,za,zb)
            realSpeed = self.fromDacToSpeed(za,zb,rs,t6t)
            culprit.valueChanged.disconnect()
            culprit.setValue(realSpeed)
            culprit.valueChanged.connect(self.manageSpeedUpdate)

        else:
            count = 2
            for s in  self.speedGroups[culprit][3:]:
                speed = s.value()
                stopMe = (za == 0 and zb == 0) or speed == 0
                if stopMe:
                    count -= 1
                    if count == 0:
                        return None
                    continue
                rs,t6t = self.speedToDacStep(speed,za,zb)
                realSpeed = self.fromDacToSpeed(za,zb,rs,t6t)
                s.valueChanged.disconnect()
                s.setValue(realSpeed)
                s.valueChanged.connect(self.manageSpeedUpdate)


    def speedToDacStep(self, speed, za, zb):

        totVrange = abs(self.systemDict['zMaxV']-self.systemDict['zMinV'])
        vrange = self.zNmtoVRel(abs(za-zb))
        totSteps = 2**int(self.privates['dacbits'])
        t6 = float(self.privates['t6'])
        speedV = self.zNmtoVRel(speed)
        dt = vrange/speedV
        vMinStep = totVrange/totSteps
        nSteps = dt/t6
        vStep = vrange/nSteps
        vStepDacEquiv = vStep/vMinStep
        if vStepDacEquiv > 0.5:
            realVStepDacEquiv = round(vStepDacEquiv)
            numT6Ticks4DacStep = 1
        else:
            realVStepDacEquiv = 1
            numT6Ticks4DacStep = round(1/vStepDacEquiv)
        return realVStepDacEquiv,numT6Ticks4DacStep


    def fromDacToSpeed(self, za, zb,realVStepDacEquiv,numT6Ticks4DacStep):

        totVrange = abs(self.systemDict['zMaxV']-self.systemDict['zMinV'])
        vrange = self.zNmtoVRel(abs(za-zb))
        totSteps = 2**int(self.privates['dacbits'])
        t6 = float(self.privates['t6'])
        vMinStep = totVrange/totSteps

        realVStep = realVStepDacEquiv*vMinStep
        realNSteps = int(vrange/realVStep)
        realDt = realNSteps*t6
        realSpeedV = vrange/realDt/numT6Ticks4DacStep

        return self.zVtoNmRel(realSpeedV)

    
    def createSpiral(self,delta1,delta2,pointsNr):
        
        spiral = []
        angle = 0.0
        limit = 1
        count = 0
        
        for i in range(pointsNr):
            p1 = [np.cos(angle)*delta1,np.sin(angle)*delta2]
            spiral.append(p1)
            count += 1
            if count == limit:
                angle += np.pi/2
                if angle%np.pi == 0:
                    limit += 1
        
        return spiral       
        
    
    def startExperiment(self,segments):

        self.segmentsToDo = segments
        
        self.currentCurve = curve.curve()

        self.zTrigBase = self.zPiezoNumDbl.value()*1000
        self.fTrigBase = 0
        
        self.curveDir = self.dirLine.text() if self.dirLine.text() != '' else self.curveDir
        if not exists(self.curveDir):
            makedirs(self.curveDir)
        self.baseCurveName = self.fileNameRootLine.text() if self.fileNameRootLine.text() != '' else self.baseCurveName
        self.currentCurvePath = join(self.curveDir,(self.baseCurveName+'_pt'+str(self.currentPtNum)+'_c'+str(self.currentCurveNum)+'.txt'))
        self.currentCurve.k = self.kNumDbl.value()
        self.currentCurve.filename = self.currentCurvePath
        self.currentCurve.save(self.currentCurvePath)
        self.mapPoints = self.createSpiral(self.xStepNumMapNum.value(), self.yStepNumMapNum.value(), self.pointsToDo)
        
        self.currentCurveNum = 0
        self.currentPtNum = 0
        self.currentSeg = 0
        
        self.remoteProg.setMaximum(self.curvesToDo*self.pointsToDo-1)
        self.experimentRds()
        
        self.expInProgress = True
        self.currentSaver = SaveThread(self)
        self.currentSaver.start()
        self.curveData.stateChanged.connect(self.segmentDone)
        self.plottedSegs,self.ramblingPlot = self.initCurvePlot(len(self.segmentsToDo)-1)
        self.curveData.chunkReceived.connect(self.ramblingPlotManager)
        self.xyRes.respReceived.connect(self.doSegment)

        self.xyCmd.send('GZ',[])
    
    
    def initCurvePlot(self,segNum):
        
        self.centralPlot.clear()
        plots = []
        n = len(self.pens)
        for i in range(len(self.segmentsToDo)):
            plots.append(self.centralPlot.plot([],[],pen=self.pens[i%n])),#i,i+1,i+2],[i,i*2,i*3],pen=self.pens[i%n]))
        ramblingPlot = self.centralPlot.plot([],[],pen=self.ramblingPen)
        return plots, ramblingPlot
    
    
    def clearPlot(self):
        
        for p in self.plottedSegs:
            p.setData([],[])
    
    
    def ramblingPlotManager(self,v):
        
        data = np.array(v)
        self.ramblingPlot.setData(self.zVtoNm(data[1,:]),data[2,:]/self.deflectionToV)
            
    
    def doSegment(self):

        segment = self.segmentsToDo[self.currentSeg]
        directionSign = (-1)**(int(segment['direction'] == 3))
        zDeltaSign = self.nearFar*directionSign
        zTrigger = self.zNmtoV(self.zTrigBase + segment['zLim']*zDeltaSign)
        fTrigger = (self.fTrigBase + segment['fLim']*directionSign)*self.deflectionToV
        tTrigger = segment['holdT']
        
        zTriggerEnabled = int(zTrigger != 0)
        fTriggerEnabled = 0#int(fTrigger != 0)
        tTriggerEnabled = int(segment['speed'] == 0)

        self.curveIntpr.setTriggersSwitch(tTriggerEnabled,zTriggerEnabled,fTriggerEnabled)
        self.curveIntpr.setZposStopTrig(zTrigger,int(zDeltaSign<0))
        self.curveIntpr.setDeflStopTrig(fTrigger,int(directionSign*self.deflSign<0))
        self.curveIntpr.setTimeStopTrig(tTrigger,0)

        if segment['type'] == 'Fconst':
            self.curveIntpr.setSetPoint(self.fTrigBase*self.deflectionToV)
        elif segment['type'] != 'Fconst' and segment['type'] != 'Zconst':
            rds,t6t = self.speedToDacStep(segment['speed'],0.0,segment['zLim'])
            self.curveIntpr.setZramp(rds,t6t)
            self.curveIntpr.setZrampSign(int(zDeltaSign<0))
        self.curveIntpr.startSegment(segment['type'])
    
        
    def segmentDone(self,v):
        if not v:
            tempQueue = self.curveData.queue[0]
            self.currZ,self.currF = self.emptyDataQueue(tempQueue)
            self.zTrigBase = self.currZ[-1]
            self.fTrigBase = np.mean(self.currF[-10:])
            if self.currentSeg > 0:
                self.currentSaver.waitingInLineZ.append(self.currZ)
                self.currentSaver.waitingInLineF.append(self.currF)
                self.currentSaver.segParams.append(self.segmentsToDo[self.currentSeg])
                self.currentSaver.curves.append(self.currentCurve)
            del self.curveData.queue[0]
            self.cycleExp()


    def emptyDataQueue(self,q):

        d = q.queue
        data = np.array(d)
        zv = data[:,1]
        fv = data[:,2]
        z = self.zVtoNm(zv)
        f = fv/self.deflectionToV

        return z,f
        
        
    def cycleExp(self):
        if self.currentSeg > 0:
            self.plottedSegs[self.currentSeg-1].setData(self.currZ[::],self.currF[::])
        
        self.currentSeg += 1
        if self.currentSeg == len(self.segmentsToDo):
            self.currentCurve = curve.curve()
            self.clearPlot()
            self.currentCurveNum += 1
            self.currentSeg = 1
            if self.currentCurveNum == self.curvesToDo:
                if self.currentPtNum+1 == self.pointsToDo:
                    self.curveData.stateChanged.disconnect()
                    self.remoteStop()
                    return 
                self.currentPtNum += 1
                self.currentCurveNum = 0
                self.currentCurvePath = join(self.curveDir,(self.baseCurveName+'_pt'+str(self.currentPtNum)+'_c'+str(self.currentCurveNum)+'.txt'))
                self.currentCurve.filename = self.currentCurvePath
                self.currentCurve.k = self.kNumDbl.value()
                self.currentCurve.save(self.currentCurvePath)
                self.experimentRds()
                self.makeAstep(self.mapPoints[self.currentPtNum][0], self.mapPoints[self.currentPtNum][1])
            else:
                self.currentCurvePath = join(self.curveDir,(self.baseCurveName+'_pt'+str(self.currentPtNum)+'_c'+str(self.currentCurveNum)+'.txt'))
                self.currentCurve.filename = self.currentCurvePath
                self.currentCurve.k = self.kNumDbl.value()
                self.currentCurve.save(self.currentCurvePath)
                self.experimentRds()
                self.doSegment()
        else:
            self.doSegment()
        
    
    def fvsd(self):
        self.rdsLine.setText('FvsD curve')
        self.pointsToDo = 1
        self.curvesToDo = self.curveNumNum.value()
        seg = {}

        self.zTrigBase = self.zPiezoNumDbl.value()*1000

        seg['zLim'] = abs(self.startZNumDbl.value()-self.zTrigBase)
        seg['fLim'] = 0
        seg['speed'] = self.toStartSpeed
        seg['direction'] = 2+1*(int((self.startZNumDbl.value()>self.zTrigBase)))#(self.startZNumDbl.value()>self.zTrigBase) if self.nearFar<0 else (self.startZNumDbl.value()<self.zTrigBase)))
        seg['holdT'] = 0
        seg['type'] = 'Vconst'
        tempSegsList = ([seg] if seg['zLim'] != 0.0 else [])+self.getStandardSeg()
        self.startExperiment(tempSegsList)
    
    
    def fvsdMap(self):
        self.rdsLine.setText('FvsD map')
        self.pointsToDo = self.ptNumMapNum.value()
        self.curvesToDo = self.curveNumNum.value()
        seg = {}
        seg['zLim'] = self.startZNumDbl.value()
        seg['fLim'] = 0
        seg['speed'] = self.toStartSpeed
        seg['direction'] = 2
        seg['holdT'] = 0
        seg['type'] = 'Vconst'
        
        tempSegsList = [seg]+self.getStandardSeg()
        self.startExperiment(tempSegsList)
    
    
    def custom(self):
        self.rdsLine.setText('Custom curve')
        self.pointsToDo = 1
        self.curvesToDo = self.curveNumcNum.value()
        
        seg = {}
        seg['zLim'] = self.startZcNumDbl.value()
        seg['fLim'] = 0
        seg['speed'] = self.toStartSpeed
        seg['direction'] = 2
        seg['holdT'] = 0
        seg['type'] = 'Vconst'
        
        tempSegsList = [seg]+self.custFvsdSegs
        self.startExperiment(tempSegsList)
    
    
    def customMap(self):
        self.rdsLine.setText('Custom map')
        self.pointsToDo = self.ptNumMapNum.value()
        self.curvesToDo = self.curveNumcNum.value()
        seg = {}
        seg['zLim'] = self.startZcNumDbl.value()
        seg['fLim'] = 0
        seg['speed'] = self.toStartSpeed
        seg['direction'] = 2
        seg['holdT'] = 0
        seg['type'] = 'Vconst'
        
        tempSegsList = [seg]+self.custFvsdSegs
        self.startExperiment(tempSegsList)
    
    
    def stopExperiment(self):
        
        self.expInProgress = False
        self.xyRes.respReceived.disconnect()
        self.currentSaver.go = False
        self.xyCmd.send('S',[])
        try:
            self.curveData.chunkReceived.disconnect()
        except Exception as e:
            print(e.message)

        self.goToRest()
        
    
    def goToRest(self):
        
        self.rdsLine.setText('')
        self.curveIntpr.goToRest()
    
    
    def experimentRds(self):
        
        self.rdsLine.setText('Curve: ' + str(self.currentCurveNum+1) + '; Point: ' + str(self.currentPtNum+1))
        self.remoteProg.setValue(self.curvesToDo*self.currentPtNum+self.currentCurveNum)
        
        
    def actionNdocksConnections(self):
        
        self.action_Motors.changed.connect(self.dockMng)
        self.motorsDock.visibilityChanged.connect(self.dockMng)
        
        self.action_Settings.changed.connect(self.dockMng)
        self.settingsDock.visibilityChanged.connect(self.dockMng)
        
        self.action_Remote.changed.connect(self.dockMng)
        self.remoteDock.visibilityChanged.connect(self.dockMng)
        
        self.action_QPD_and_piezo.changed.connect(self.dockMng)
        self.qpdNpiezoDock.visibilityChanged.connect(self.dockMng)
        
        self.action_Edit_config.triggered.connect(self.showDial)
        self.action_Exit.triggered.connect(self.close)
        
        self.action_Save_parameters.triggered.connect(self.saveParams)
        self.action_Load_parameters.triggered.connect(self.loadParams)
        
        self.action_Open_SiMPlE.triggered.connect(self.startAnalyzing)
        
    
    def buttonsConnections(self):
        
        self.addSegBtn.clicked.connect(self.addSeg)
        self.removeSegBtn.clicked.connect(self.removeSeg)
        self.updateSegBtn.clicked.connect(self.updateSeg)
        self.showZTravelBtn.clicked.connect(self.showDial)
        self.playBtn.clicked.connect(self.remotePlay)
        self.stopBtn.clicked.connect(self.remoteStop)
        
        # Epz Parameters buttons connections
        
        self.uploadSetPtBtn.clicked.connect(self.uploadEpzParam)
        self.uploadPGainBtn.clicked.connect(self.uploadEpzParam)
        self.uploadIGainBtn.clicked.connect(self.uploadEpzParam)
        self.uploadFbBtn.clicked.connect(self.uploadEpzParam)
        self.uploadKdBtn.clicked.connect(self.uploadEpzParam)
        self.uploadCalibStimZOffsetBtn.clicked.connect(self.uploadEpzParam)
        self.uploadCalibStimAmplBtn.clicked.connect(self.uploadEpzParam)
        self.uploadCalibStimZOffsetBtn.clicked.connect(self.uploadEpzParam)
        self.uploadCalibStimFreqBtn.clicked.connect(self.uploadEpzParam)
        self.uploadCalibStimBtn.clicked.connect(self.uploadEpzParam)
        self.uploadKBtn.clicked.connect(self.uploadEpzParam)
        self.uploadPkStartFreqBtn.clicked.connect(self.uploadEpzParam)
        self.uploadPkEndFreqBtn.clicked.connect(self.uploadEpzParam)
        self.uploadClLenBtn.clicked.connect(self.uploadEpzParam)
        self.uploadClWidBtn.clicked.connect(self.uploadEpzParam)
        self.uploadMediumDensBtn.clicked.connect(self.uploadEpzParam)
        self.uploadMediumViscBtn.clicked.connect(self.uploadEpzParam)
        self.uploadKCalibBtn.clicked.connect(self.uploadEpzParam)
        self.uploadMaxFBtn.clicked.connect(self.uploadEpzParam)
        self.uploadStartZBtn.clicked.connect(self.uploadEpzParam)
        self.uploadEndZBtn.clicked.connect(self.uploadEpzParam)
        self.uploadAppSpeedBtn.clicked.connect(self.uploadEpzParam)
        self.uploadRetrSpeedBtn.clicked.connect(self.uploadEpzParam)
        self.uploadHoldTimeBtn.clicked.connect(self.uploadEpzParam)
        self.uploadFvsdBtn.clicked.connect(self.uploadEpzParam)
        self.uploadStartZcBtn.clicked.connect(self.uploadEpzParam)
        
        self.altZSegBtn.clicked.connect(self.changeDir)
        self.altFSegBtn.clicked.connect(self.changeDir)
        self.farSegBtn.clicked.connect(self.changeDir)
        self.nearSegBtn.clicked.connect(self.changeDir)
        
        self.xPlusBtn.clicked.connect(self.motorRemoteCmd)
        self.xMinusBtn.clicked.connect(self.motorRemoteCmd)
        self.yPlusBtn.clicked.connect(self.motorRemoteCmd)
        self.yMinusBtn.clicked.connect(self.motorRemoteCmd)
        self.goCenterBtn.clicked.connect(self.motorRemoteCmd)
        self.resetXYBtn.clicked.connect(self.motorRemoteCmd)
        
        
    def epzConnections(self):
        
        self.curveData.yDataReceived.connect(self.sendZ)
        #self.curveData.chunkReceived.connect(self.sendZ)
        #self.monitData.chunkReceived.connect(self.updateQPD)
        self.monitData.xDataReceived.connect(self.deflNumDbl.setValue)
        self.monitData.yDataReceived.connect(self.torsNumDbl.setValue)
        self.monitData.zDataReceived.connect(self.sumNumDbl.setValue)
        
        
    def genericConnetions(self):
        
        self.deflNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.torsNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.sumNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.zPiezoNumDbl.valueChanged.connect(self.zMonitProg)
        self.browseBtn.clicked.connect(self.getDataDir)
        self.segCmbBox.currentIndexChanged.connect(self.showSeg)
        self.kdNumDbl.valueChanged.connect(self.changeRefDefl)
        self.kNumDbl.valueChanged.connect(self.changeRefDefl)
        self.appSpeedNumDbl.valueChanged.connect(self.manageSpeedUpdate)
        self.retrSpeedNumDbl.valueChanged.connect(self.manageSpeedUpdate)
        self.speedcNumDbl.valueChanged.connect(self.manageSpeedUpdate)
        self.endZcNumDbl.valueChanged.connect(self.manageSpeedUpdate)
        self.endZNumDbl.valueChanged.connect(self.manageSpeedUpdate)
        self.startZNumDbl.valueChanged.connect(self.manageSpeedUpdate)



    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Do you really want to close CoMPlEx?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.curveIntpr.stopDev()
            self.monitIntpr.stopDev()
            self.motorsDock.visibilityChanged.disconnect()
            self.settingsDock.visibilityChanged.disconnect()
            self.remoteDock.visibilityChanged.disconnect()
            self.qpdNpiezoDock.visibilityChanged.disconnect()
            event.accept()
        else:
            event.ignore()
        
    
class SaveThread(QThread):
    
    def __init__(self,parent):
        
        super(SaveThread,self).__init__()
        self.waitingInLineZ = []
        self.waitingInLineF = []
        self.segParams = []
        self.curves = []
        self.go = True
        self.parent = parent
    
    
    def run(self):

        while self.go or len(self.waitingInLineZ)>0:
            if len(self.waitingInLineZ)>0:
                newz = self.waitingInLineZ[0]
                newf = self.waitingInLineF[0]
                tempSeg = self.segParams[0]
                curve = self.curves[0]
                emptySeg = segment.segment(list(newz),list(newf))
                emptySeg.k = self.parent.kNumDbl.value()
                emptySeg.speed = tempSeg['speed']
                emptySeg.direction = 'hold' if tempSeg['direction'] < 2 else ('far' if tempSeg['direction'] == 2 else 'near')
                emptySeg.type = tempSeg['type']
                del self.waitingInLineZ[0]
                del self.waitingInLineF[0]
                del self.segParams[0]
                del self.curves[0]
                curve.appendToFile(emptySeg)
                
            sleep(0.01)
            
            
            