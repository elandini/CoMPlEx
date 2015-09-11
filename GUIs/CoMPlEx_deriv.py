from GUIs.CoMPlEx_GUI import *
from GUIs.hwConfig_deriv import *
from GUIs.zPath_deriv import *

from threading import Thread

import PyQt4.QtGui as qg
from PyQt4 import QtCore
from PyQt4.QtGui import QDialog, QFileDialog
from PyQt4.QtGui import QMainWindow
import pyqtgraph as pg

from os import makedirs
from subprocess import Popen
from os.path import splitext, split, join, exists
#from ConfigParser import ConfigParser
from configparser import ConfigParser
import numpy as np

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

from libs.epz import epz
from libs.curveLib import curve,segment

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

CHUNK = 20

class CoMPlEx_main(QMainWindow,Ui_CoMPlEx_GUI):
    
    channels = ['Engage','Calib QPD','Calib K','FvsD curve','FvsD map','Custom curve','Custom map']
    
    def __init__(self,parent = None):
    
        super(CoMPlEx_main,self).__init__(parent)
        self.setupUi(self)
        
        icon = qg.QIcon()
        icon.addPixmap(qg.QPixmap(_fromUtf8("GUIs/Icons/altZ.bmp")), qg.QIcon.Normal, qg.QIcon.Off)
        self.altZSegBtn.setIcon(icon)
        
        icon1 = qg.QIcon()
        icon1.addPixmap(qg.QPixmap(_fromUtf8("GUIs/Icons/altF.bmp")), qg.QIcon.Normal, qg.QIcon.Off)
        self.altFSegBtn.setIcon(icon1)
        
        icon2 = qg.QIcon()
        icon2.addPixmap(qg.QPixmap(_fromUtf8("GUIs/Icons/far.bmp")), qg.QIcon.Normal, qg.QIcon.Off)
        self.farSegBtn.setIcon(icon2)
        
        icon3 = qg.QIcon()
        icon3.addPixmap(qg.QPixmap(_fromUtf8("GUIs/Icons/near.bmp")), qg.QIcon.Normal, qg.QIcon.Off)
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
        
        self.programs = [self.engage,self.calibQPD,self.calibK,self.fvsd,self.fvsdMap,self.custom,self.customMap]
        self.stops = [self.stopSingle,self.stopMap]
        
        self.cfgFile = str(QFileDialog.getOpenFileName(self,'Select a configuration file',filter='Ini (*.ini)'))
        if self.cfgFile == '':
            self.cfgFile = 'config/defaultCfg.ini'
        self.channelCmbBox.clear()
        self.channelMng('Engage')
        self.hwDial = hwConfig_dial(self,self.cfgFile)
        self.laserSpot = self.alignPlot.plot([0],[0],pen = None, symbol = 'o', symbolPen = 'r', symbolSize = 50, symbolBrush = qg.QColor(0,0,0,128))
        self.alignPlot.plot([0],[0],pen = None, symbol = 'o', symbolPen = {'color':'b','width':2}, symbolSize = 50, symbolBrush = qg.QColor(255,255,255,0))
        self.alignPlot.plotItem.showAxis('top',True)
        self.alignPlot.plotItem.showAxis('right',True)
        self.alignPlot.plotItem.showGrid(True,True,1)
        self.alignPlot.plotItem.setRange(xRange = [-10,10],yRange = [-10,10])
        self.alignPlot.plotItem.setMouseEnabled(False,False)
        
        self.curveEnv = epz.Environment()
        self.monitEnv = epz.Environment()
        
        self.currentSpeed = 0.0
        self.currentDirection = 'far'
        self.currentType = 'Zconst'
        self.currentCurve = None
        self.currentCurveNum = 0
        self.currentPtNum = 0
        self.saveMe = False
        
        self.applyConfig()
        self.epzConnect()
        self.epzConnections()
        self.actionNdocksConnections()
        self.buttonsConnections()
        self.genericConnetions()
    
    
    def channelMng(self,channel,operation = '+'):
        
        if operation == '+':
            if channel in self.channels:
                self.channelCmbBox.addItem(channel)
                del self.channels[self.channels.index(channel)]
        elif operation == '-':
            if channel not in self.channels:
                self.channelCmbBox.removeItem(self.channelCmbBox.findText(channel))
                self.channels.append(channel)
    
    
    def getParamsDict(self):
        
        baseDict = {qg.QSpinBox:['NUM','.value()','.setValue(',[]],qg.QDoubleSpinBox:['DBL','.value()','.setValue(',[]],
                    qg.QLineEdit:['LINE','.text()','.setText(',[]],qg.QCheckBox:['CKBOX','.isChecked()','.setChecked(',[]]}
        
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
    
    
    def applyConfig(self):
        
        if self.cfgFile != self.hwDial.cfgFile:
            self.cfgFile = self.hwDial.cfgFile
        
        parser = ConfigParser()
        parser.read(self.cfgFile)
        
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
        
        self.curveEnv.pubport = self.forwarderPubPort
        self.curveEnv.subport = self.forwarderSubPort
        self.curveEnv.device = self.curveName
        self.curveEnv.epserver = self.forwarderIP
        self.monitEnv.pubport = self.forwarderPubPort
        self.monitEnv.subport = self.forwarderSubPort
        self.monitEnv.device = self.monitName
        self.monitEnv.epserver = self.forwarderIP
        
        zM = float(parser.get('PIEZO','zmax'))*1000
        zm = float(parser.get('PIEZO','zmin'))*1000
        
        zvM = float(parser.get('PIEZO','vmax'))
        zvm = float(parser.get('PIEZO','vmin'))
        
        self.zVtoNm = lambda x: ((x-zvm)/(zvM-zvm)*(zM-zm)+zm) 
        
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
        self.nearFar = (-1)**(int(parser.get('PIEZO','nearfar')))
        self.zPiezoProg.setInvertedAppearance(self.nearFar<0)
        
        self.simplePath = parser.get('SIMPLE','path')
        self.action_Open_SiMPlE.setEnabled(len(self.simplePath) > 2)
        
        
    def epzConnect(self):
        
        self.curveData = epz.QtDATA(self.curveEnv)
        self.monitData = epz.QtDATA(self.monitEnv)
        
        self.curveCmd = epz.CMD(self.curveEnv)
        self.monitCmd = epz.CMD(self.monitEnv)
        
        self.xyCmd = epz.CMD(self.monitEnv)
        self.xyCmd.command = self.xyCmdTag
        
        self.xyRes = epz.QtCMDREC(self.monitEnv)
        self.xyRes.tag = self.xyResTag
        
        self.curveData.notify = True
        self.curveData.save = False
        self.monitData.notify = True
        self.monitData.save = False
        
        self.curveData.chunk = CHUNK
        self.monitData.chunk = CHUNK
        
        self.curveData.start()
        self.curveCmd.send('g',1)
        self.monitData.start()
        self.monitCmd.send('g',1)
        self.xyRes.start()
    
    
    def saveParams(self):
        
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
            for i in xrange(len(sDict[k][3])):
                paramsParser.set(sDict[k][0], sDict[k][3][i], str(eval('self.'+sDict[k][3][i]+sDict[k][1])))
        
        paramsParser.write(paramsFile)
        paramsFile.close()
        
    
    def loadParams(self):
        
        parFileName = str(QFileDialog.getOpenFileName(self,'Choose a parameters file',filter='Parameters Files (*.par)'))
        if parFileName == '':
            return None
        lDict = self.getParamsDict()
        #paramsFile = open(parFileName,'r')
        paramsParser = ConfigParser()
        paramsParser.read(parFileName)
        if paramsParser.get('MISC', 'afm') != self.cfgFile:
            warning = qg.QMessageBox(self)
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
        
    
    def uploadEpzParam(self):
        
        culprit = self.sender()
        
        
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
            self.hwDial.exec_()
        elif culprit is self.shoZTravelBtn:
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
            self.laserSpot.setSymbolBrush(qg.QColor(int(25.5*newVal),0,0,128))
        
        
    def updateQPD(self,v):
        
        #deflValue = np.max(np.array(v[0])) REAL
        deflValue = np.max(np.array(v[1]))
        sumValue = np.max(np.array(v[2]))
        torsValue = np.max(np.array(v[1]))
        
        # CANCELLA NELLA VERSIONE DEFINITIVA
        deflValue *=10
        sumValue *=10
        torsValue *=10
        # CANCELLA NELLA VERSIONE DEFINITIVA
        
        self.deflNumDbl.setValue(deflValue)
        self.torsNumDbl.setValue(torsValue)
        self.sumNumDbl.setValue(sumValue)
   
        
    def sendZ(self,v):
        
        zValue = np.max(np.array(v[1]))
        
        # CANCELLA NELLA VERSIONE DEFINITIVA
        zValue *=10
        # CANCELLA NELLA VERSIONE DEFINITIVA
        
        self.zPiezoNumDbl.setValue(zValue)
    
        
    def close(self):
        
        self.motorsDock.visibilityChanged.disconnect()
        self.settingsDock.visibilityChanged.disconnect()
        self.remoteDock.visibilityChanged.disconnect()
        self.qpdNpiezoDock.visibilityChanged.disconnect()
        
        super(CoMPlEx_main,self).close()
        
        
    def startAnalyzing(self):
        
        p = Popen('python3 '+self.simplePath)
    
    
    def getStandardSeg(self):
        
        stdSegments = []
        
        seg = {}
        
        seg['zLim'] = self.endZNumDbl.value()
        seg['fLim'] = self.endFNumDbl.value()
        seg['speed'] = self.appSpeedNumDbl.value()
        seg['direction'] = 3
        seg['holdT'] = 0
        
        stdSegments.append(seg)
        
        seg = {}
        
        seg['zLim'] = self.endZNumDbl.value()
        seg['fLim'] = self.endFNumDbl.value()
        seg['speed'] = self.appSpeedNumDbl.value()
        seg['direction'] = 3
        seg['holdT'] = 0
        
        
    def addSeg(self):
        
        seg = {}
        
        seg['zLim'] = self.endZcNumDbl.value()
        seg['fLim'] = self.endFcNumDbl.value()
        seg['speed'] = self.speedcNumDbl.value()
        seg['direction'] = self.getDir()
        seg['holdT'] = self.holdTimecNumDbl.value()
        
        self.custFvsdSegs.append(seg)
        
        self.segCmbBox.addItem('Segment: ' + str(self.segCmbBox.count()))
        
        if not self.removeSegBtn.isEnabled():
            self.removeSegBtn.setEnabled(True)
            self.updateSegBtn.setEnabled(True)
        self.segCmbBox.setCurrentIndex(self.segCmbBox.count()-1)
        
        
    def removeSeg(self):
        
        junkInd = self.segCmbBox.currentIndex()
        for i in xrange(self.segCmbBox.count()-(junkInd+1)):
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
        
        self.custFvsdSegs[ind]['zLim'] = self.endZcNumDbl.value()
        self.custFvsdSegs[ind]['fLim'] = self.endFcNumDbl.value()
        self.custFvsdSegs[ind]['speed'] = self.speedcNumDbl.value()
        self.custFvsdSegs[ind]['direction'] = self.getDir()
        self.custFvsdSegs[ind]['holdT'] = self.holdTimecNumDbl.value()
        self.custFvsdSegs[ind]['fbOn'] = self.altFSegBtn.isChecked()
            
            
    def plotSeg(self):
        
        zPathDial = zPath_dial(self,self.custFvsdSegs,self.startZcNumDbl.value())
        zPathDial.exec_()
        
        
    def remotePlay(self):
        
        channel = self.channelCmbBox.currentIndex()
        
        self.programs[channel]()
        
        
    def remoteStop(self):
        
        channel = self.channelCmbBox.currentIndex()
        
        if channel == 4 or channel == 6:
            self.stopMap()
        else:
            self.stopSingle()
    
    
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
    
    
    def engage(self):
        
        self.channelMng('Calib QPD')
        self.rdsLine.setText('Engaging...')
        
        
    def calibQPD(self):
        
        self.channelMng('Calib K')
        self.rdsLine.setText('QPD calibration')
        
        
    def calibK(self):
        
        self.channelMng('FvsD curve')
        self.channelMng('FvsD map')
        self.channelMng('Custom curve')
        self.channelMng('Custom map')
        self.rdsLine.setText('Elastic constant calibration')
        
    
    def startExperiment(self):
        
        culprit = self.sender()
        self.xyCmd.send('GZ',[])
        
        self.currentCurve = curve.curve()
        if not exists(self.dirLine.text()):
            makedirs(self.dirLine.text())
        self.currentCurvePath = join(self.dirLine.text(),(self.fileNameRootLine+'_pt'+str(self.currentPtNum)+'_c'+str(self.currentCurveNum)+'.txt'))
        
        savingT = Thread(self.saveSegment)
        savingT.start()
        
    
    
    def saveSegment(self):
        while self.expInProgress:
            if self.saveMe:
                tempQueue = self.curveData.queue[0]
                del self.curveData.queue[0]
                self.newz,self.newf = self.emptyDataQueue(tempQueue)
                emptySeg = segment.segment(self.newz,self.newf)
                emptySeg.k = self.kNumDbl.value()
                emptySeg.speed = self.currentSpeed
                emptySeg.direction = self.currentDirection
                emptySeg.type = self.currentType
        
                curve.append(emptySeg)
                curve.save(self.currentCurvePath)
                
                self.saveMe = False
    
    
    def emptyDataQueue(self,q):
        
        t,zv,fv = []
        while q.qsize()>0:
            temp = q.get()
            t.append(temp[0])
            zv.append(temp[1])
            fv.append(temp[2])
        z = self.zVtoNm(np.array(zv))
        f = np.array(fv)*self.kNumDbl.value()*self.kdNumDbl.value()
        
        return z,f
    
        
    def segmentDone(self):
        
        self.saveMe = True
        
        pass
        
    
    def fvsd(self):
        self.rdsLine.setText('FvsD curve')
    
    
    def fvsdMap(self):
        self.rdsLine.setText('FvsD map')
    
    
    def custom(self):
        self.rdsLine.setText('Custom curve')
    
    
    def customMap(self):
        self.rdsLine.setText('Custom map')
    
    
    def stopSingle(self):
        self.rdsLine.setText('')
    
    
    def stopMap(self):
        self.rdsLine.setText('')
        
        
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
        
        self.curveData.chunkReceived.connect(self.sendZ)
        self.monitData.chunkReceived.connect(self.updateQPD)
        
        
    def genericConnetions(self):
        
        self.deflNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.torsNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.sumNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.zPiezoNumDbl.valueChanged.connect(self.zMonitProg)
        self.browseBtn.clicked.connect(self.getDataDir)
        self.segCmbBox.currentIndexChanged.connect(self.showSeg)
        
        
        