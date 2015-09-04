from GUIs.CoMPlEx_GUI import *
from GUIs.hwConfig_deriv import *
from GUIs.hwConfig_deriv import *

from threading import Thread

import PyQt4.QtGui as qg
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

CHUNK = 20

class CoMPlEx_main(QMainWindow,Ui_CoMPlEx_GUI):
    
    def __init__(self,parent = None):
    
        super(CoMPlEx_main,self).__init__(parent)
        self.setupUi(self)
        
        self.actionNdockDict = {self.action_Motors:[self.motorsDock,'isChecked','setVisible','visibilityChanged'],
                                self.action_Settings:[self.settingsDock,'isChecked','setVisible','visibilityChanged'],
                                self.action_Remote:[self.remoteDock,'isChecked','setVisible','visibilityChanged'],
                                self.action_QPD_and_piezo:[self.qpdNpiezoDock,'isChecked','setVisible','visibilityChanged'],
                                self.motorsDock:[self.action_Motors,'isVisible','setChecked','changed'],
                                self.settingsDock:[self.action_Settings,'isVisible','setChecked','changed'],
                                self.remoteDock:[self.action_Remote,'isVisible','setChecked','changed'],
                                self.qpdNpiezoDock:[self.action_QPD_and_piezo,'isVisible','setChecked','changed']}
        
        self.custFvsdSegs = []
        
        self.cfgFile = str(QFileDialog.getOpenFileName(self,'Select a configuration file',filter='Ini (*.ini)'))
        if self.cfgFile == '':
            self.cfgFile = 'config/defaultCfg.ini'
        self.channelCmbBox.clear()
        self.channelCmbBox.addItem('Engage')
        self.hwDial = hwConfig_dial(self,self.cfgFile)
        self.laserSpot = self.alignPlot.plot([0],[0],pen = None, symbol = 'o', symbolPen = 'r', symbolSize = 50, symbolBrush = qg.QColor(0,0,0,128))
        self.alignPlot.plot([0],[0],pen = None, symbol = 'o', symbolPen = {'color':'b','width':2}, symbolSize = 50, symbolBrush = qg.QColor(255,255,255,0))
        self.alignPlot.plotItem.showAxis('top',True)
        self.alignPlot.plotItem.showAxis('right',True)
        self.alignPlot.plotItem.showGrid(True,True,1)
        self.alignPlot.plotItem.setRange(xRange = [-10,10],yRange = [-10,10])
        self.alignPlot.plotItem.setMouseEnabled(False,False)
        
        self.deflEnv = epz.Environment()
        self.torsEnv = epz.Environment()
        self.sumEnv = epz.Environment()
        self.zEnv = epz.Environment()
        
        self.applyConfig()
        self.epzConnect()
        self.epzConnections()
        self.actionNdocksConnections()
        self.buttonsConnections()
        self.genericConnetions()
    
    
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
        
        self.forwarderIP = parser.get('CONN','afmip')
        self.forwarderPubPort = parser.get('CONN','afmpubport')
        self.forwarderSubPort = parser.get('CONN','afmsubport')
        self.deflName = parser.get('CONN','deflname')
        self.torsName = parser.get('CONN','torsname')
        self.sumName = parser.get('CONN','sumname')
        self.zName = parser.get('CONN','zname')
        self.xyPort = parser.get('CONN','xyport')
        self.zPort = parser.get('CONN','zport')
        
        self.deflEnv.pubport = self.forwarderPubPort
        self.deflEnv.subport = self.forwarderSubPort
        self.deflEnv.device = self.deflName
        self.deflEnv.epserver = self.forwarderIP
        self.torsEnv.pubport = self.forwarderPubPort
        self.torsEnv.subport = self.forwarderSubPort
        self.torsEnv.device = self.torsName
        self.torsEnv.epserver = self.forwarderIP
        self.sumEnv.pubport = self.forwarderPubPort
        self.sumEnv.subport = self.forwarderSubPort
        self.sumEnv.device = self.sumName
        self.sumEnv.epserver = self.forwarderIP
        self.zEnv.pubport = self.forwarderPubPort
        self.zEnv.subport = self.forwarderSubPort
        self.zEnv.device = self.zName
        self.zEnv.epserver = self.forwarderIP
        
        zM = float(parser.get('PIEZO','zmax'))*1000
        zm = float(parser.get('PIEZO','zmin'))*1000
        
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
        
        self.deflData = epz.QtDATA(self.deflEnv)
        self.torsData = epz.QtDATA(self.torsEnv)
        self.sumData = epz.QtDATA(self.sumEnv)
        self.zData = epz.QtDATA(self.zEnv)
        
        self.deflCmd = epz.CMD(self.deflEnv)
        self.torsCmd = epz.CMD(self.torsEnv)
        self.sumCmd = epz.CMD(self.sumEnv)
        self.zCmd = epz.CMD(self.zEnv)
        
        self.deflData.notify = True
        self.deflData.save = False
        self.torsData.notify = True
        self.torsData.save = False
        self.sumData.notify = True
        self.sumData.save = False
        self.zData.notify = True
        self.zData.save = False
        
        self.sumData.chunk = CHUNK
        self.deflData.chunk = CHUNK
        self.torsData.chunk = CHUNK
        self.zData.chunk = CHUNK
        
        self.sumData.start()
        self.sumCmd.send('g',1)
        self.deflData.start()
        self.deflCmd.send('g',1)
        self.torsData.start()
        self.torsCmd.send('g',1)
        self.zData.start()
        self.zCmd.send('g',1)
    
    
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
    
    
    def sendSum(self,v):
        
        sumValue = np.max(np.array(v[1]))
        
        # CANCELLA NELLA VERSIONE DEFINITIVA
        sumValue *=10
        # CANCELLA NELLA VERSIONE DEFINITIVA
        
        self.sumNumDbl.setValue(sumValue)
        
        
    def sendDefl(self,v):
        
        deflValue = np.max(np.array(v[1]))
        
        # CANCELLA NELLA VERSIONE DEFINITIVA
        deflValue *=10
        # CANCELLA NELLA VERSIONE DEFINITIVA
        
        self.deflNumDbl.setValue(deflValue)
        
        
    def sendTors(self,v):
        
        torsValue = np.max(np.array(v[2]))
        
        # CANCELLA NELLA VERSIONE DEFINITIVA
        torsValue *=10
        # CANCELLA NELLA VERSIONE DEFINITIVA
        
        self.torsNumDbl.setValue(torsValue)
        
        
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
        self.sumData.stop()
        self.deflData.stop()
        self.torsData.stop()
        self.zData.stop()
        
        super(CoMPlEx_main,self).close()
        
        
    def startAnalyzing(self):
        
        p = Popen('python3 '+self.simplePath)
        
        
    def addSeg(self):
        
        seg = {}
        
        seg['zLim'] = self.endZcNumDbl.value()
        seg['fLim'] = self.endFcNumDbl.value()
        seg['ptNum'] = self.ptNumcNum.value()
        seg['speed'] = self.speedcNumDbl.value()
        seg['direction'] = self.dircCmbBox.currentIndex()
        seg['holdT'] = self.holdTimecNumDbl.value()
        seg['fbOn'] = self.constForcecCkBox.isChecked()
        
        self.custFvsdSegs.append(seg)
        
        self.segCmbBox.addItem('Segment: ' + str(self.segCmbBox.count()))
        
        if not self.removeSegBtn.isEnabled():
            self.removeSegBtn.setEnabled(True)
        
        
    def removeSeg(self):
        
        junkInd = self.segCmbBox.currentIndex()
        for i in xrange(self.segCmbBox.count()-(junkInd+1)):
            num = i+junkInd
            self.segCmbBox.setItemText(i+junkInd+1,'Segment: '+str(num))
        self.segCmbBox.removeItem(junkInd)
        del self.custFvsdSegs[junkInd]
        self.removeSegBtn.setEnabled(len(self.custFvsdSegs))
        if len(self.custFvsdSegs):
            self.segCmbBox.setCurrentIndex(0)
        else:
            self.showSeg()
        
        
    def showSeg(self):
        if self.segCmbBox.count()==0:
            self.endZcNumDbl.setValue(0)
            self.endFcNumDbl.setValue(0)
            self.ptNumcNum.setValue(0)
            self.speedcNumDbl.setValue(0)
            self.dircCmbBox.setCurrentIndex(0)
            self.holdTimecNumDbl.setValue(0)
            self.constForcecCkBox.setChecked(False)
            
            return None
         
        seg = self.custFvsdSegs[self.segCmbBox.currentIndex()]
        self.endZcNumDbl.setValue(seg['zLim'])
        self.endFcNumDbl.setValue(seg['fLim'])
        self.ptNumcNum.setValue(seg['ptNum'])
        self.speedcNumDbl.setValue(seg['speed'])
        self.dircCmbBox.setCurrentIndex(seg['direction'])
        self.holdTimecNumDbl.setValue(seg['holdT'])
        self.constForcecCkBox.setChecked(seg['fbOn'])
        
        
    def guideSeg(self):
        
        culprit = self.sender()
        ind = culprit.currentIndex()
        
        self.speedcNumDbl.setEnabled(ind!=2)
        self.constForcecCkBox.setEnabled(ind==2)
        self.holdTimecNumDbl.setEnabled(ind==2)
        
        
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
        
        
    def epzConnections(self):
        
        self.sumData.chunkReceived.connect(self.sendSum)
        self.deflData.chunkReceived.connect(self.sendDefl)
        self.torsData.chunkReceived.connect(self.sendTors)
        self.zData.chunkReceived.connect(self.sendZ)
        
        
    def genericConnetions(self):
        
        self.deflNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.torsNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.sumNumDbl.valueChanged.connect(self.qpdMonitProgs)
        self.zPiezoNumDbl.valueChanged.connect(self.zMonitProg)
        self.browseBtn.clicked.connect(self.getDataDir)
        self.segCmbBox.currentIndexChanged.connect(self.showSeg)
        self.dircCmbBox.currentIndexChanged.connect(self.guideSeg)
        
        
        