#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        distributionViewer.py
#
# Purpose:     This module is used to read the data from serveral CSV files in 
#              data/model folder and draw the distribution diagram.
#             
# Author:      Yuancheng Liu
#
# Created:     2019/08/02
# Copyright:   NUS Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import io, sys
import csv
import time
import glob
import wx # use wx to build the UI.
import random
import numpy as np
# Import the local modules
import distributionViewGlobal as gv
import distributionViewPanel as dvp
import distributionVieweBCRun as btcRun

UPDATE_U = 1        # update time unit for test.
PERIODIC = 500      # update in every 500ms
SAMPLE_COUNT = 930  # how many sample at the Y-Axis
DEF_SIZE = (1920, 750)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionViewFrame(wx.Frame):
    """ Main frame of the distribution viewer."""
    def __init__(self, parent, id, title):
        """ Init the UI and all parameters """
        wx.Frame.__init__(self, parent, id, title, size=DEF_SIZE)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(gv.ICON_PATH, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        gv.iMainFame = self
        self.sampleCount = SAMPLE_COUNT
        self.infoWindow = None  # popup window to do the setting.
        self.updateLock = False # lock the main program update.
        self.synAdjust = True   # Synchronize adjustment on 2 display panels.
        self.displayChoice = \
            ('Type 0: Timestamping Delay',
             'Type 1: Preprocessing Delay',
             'Type 2: Disk Seek Delay',
             'Type 3: Disk Read Delay',
             'Type 4: Client Observed Delay',
             'Type 5: Input/Output Delay (Type 2 + Type 3)')
        # Init the frame UI.
        menubar = wx.MenuBar()  # Creat the function menu bar.
        menubar.Append(wx.Menu(), '&Help')
        self.SetMenuBar(menubar)
        self.SetSizer(self.buildUISizer())
        # The csv data manager.
        self.dataMgr = distributionDataMgr(self)
        # Init the thread to call experiment program.
        self.expThread = btcRun.commThread(1, "Thread-1", 1)
        # Init the periodic timer.
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms
        # Show the frame.
        self.SetDoubleBuffered(True)
        self.Refresh(False)

#--distributionViewFrame-------------------------------------------------------
    def buildUISizer(self):
        """ Init the frame user interface and return the sizer."""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        width, _ = wx.GetDisplaySize()
        appSize = (width, 700) if width == 1920 else (1600, 700)
        sizer = wx.BoxSizer(wx.VERTICAL) # main frame sizer.
        # Row idx 0: [model] experiment display selection.
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.Button(self, label='Data Source: [Model]', size=(
            140, 23)), flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        self.expMSBt = wx.Button(self, label='Setup', size=(60, 23))
        hbox0.Add(self.expMSBt, flag=flagsR, border=2)
        self.expMSBt.Bind(wx.EVT_BUTTON, self.onSetupModelExp)
        hbox0.AddSpacer(10)
        self.chartTypeCH0 = wx.ComboBox(
            self, -1, choices=self.displayChoice, style=wx.CB_READONLY)
        self.chartTypeCH0.Bind(wx.EVT_COMBOBOX, self.onChangeDMT)
        self.chartTypeCH0.SetSelection(gv.iModelType)
        hbox0.Add(self.chartTypeCH0, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        choice = ('Logarithmic scale: 10^n', 'Linear scale: Dynamic', 'Linear scale: Fixed')
        self.disModeMCB = wx.ComboBox(self, -1, choices=choice, style=wx.CB_READONLY)
        self.disModeMCB .SetSelection(0)
        self.disModeMCB.Bind(wx.EVT_COMBOBOX, self.onChangeYS)
        hbox0.Add(self.disModeMCB, flag=flagsR, border=2)
        sizer.Add(hbox0, flag=flagsR, border=2)
        # Row idx 1: display panel for the model.
        gv.iChartPanel0 = dvp.PanelChart(
            self, 3, appSize=appSize, recNum=self.sampleCount)
        sizer.Add(gv.iChartPanel0, flag=flagsR, border=2)
        sizer.AddSpacer(2)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(width, -1),
                                style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(2)
        # Row idx 2: [data] experiment display selection.
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.Button(self, label='Data Source: [Data]', size=(
            140, 23)), flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        self.expCSBt = wx.Button(self, label='Setup', size=(60, 23))
        hbox1.Add(self.expCSBt, flag=flagsR, border=2)
        self.expCSBt.Bind(wx.EVT_BUTTON, self.onSetupCheckExp)
        hbox1.AddSpacer(10)
        self.chartTypeCH1 = wx.ComboBox(
            self, -1, choices=self.displayChoice, style=wx.CB_READONLY)
        self.chartTypeCH1.Bind(wx.EVT_COMBOBOX, self.onChangeDCT)
        self.chartTypeCH1.SetSelection(gv.iDataType)
        hbox1.Add(self.chartTypeCH1, flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        self.disModeDCB =  wx.ComboBox(
            self, -1, choices=choice, style=wx.CB_READONLY)
        self.disModeDCB .SetSelection(0)
        self.disModeDCB.Bind(wx.EVT_COMBOBOX, self.onChangeYS)
        hbox1.Add(self.disModeDCB, flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        self.pauseBt = wx.Button(
            self, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        self.pauseBt.Bind(wx.EVT_BUTTON, self.reloadData)
        hbox1.Add(self.pauseBt, flag=flagsR, border=2)
        sizer.Add(hbox1, flag=flagsR, border=2)
        # Row idx 3: display panel for the model.
        gv.iChartPanel1 =  dvp.PanelChart(self, 1, appSize=appSize, recNum=self.sampleCount)
        sizer.Add(gv.iChartPanel1, flag=flagsR, border=2)
        sizer.AddSpacer(2)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(width, -1),
                                style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(2)
        # Row dix 4: display setting
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(
            self, label="Display Setting:"), flag=flagsR, border=2)
        hbox2.AddSpacer(10)
        self.updateRateCB = wx.ComboBox(
            self, -1, choices=['Update Rate: %s s' %str(i+1) for i in range(5)], style=wx.CB_READONLY)
        self.updateRateCB.SetSelection(1)
        self.updateRateCB.Bind(wx.EVT_COMBOBOX, self.onChangeUR)
        hbox2.Add(self.updateRateCB, flag=flagsR, border=2)
        hbox2.AddSpacer(10)
        self.lineStyleCB = wx.ComboBox(
            self, -1, choices=['Line Style: thin', 'Line Style: thick'], style=wx.CB_READONLY)
        self.lineStyleCB.SetSelection(0)
        self.lineStyleCB.Bind(wx.EVT_COMBOBOX, self.onChangeLS)
        hbox2.Add(self.lineStyleCB, flag=flagsR, border=2)
        hbox2.AddSpacer(10)
        self.SampleRCH0 = wx.ComboBox(
            self, -1, choices=['Sample Count: '+str((i+1)*10) for i in range(10)], style=wx.CB_READONLY)
        self.SampleRCH0.Bind(wx.EVT_COMBOBOX, self.onChangeSR)
        self.SampleRCH0.SetSelection(2)
        hbox2.Add(self.SampleRCH0, flag=flagsR, border=2)
        hbox2.AddSpacer(10)
        self.pctCB = wx.ComboBox(
            self, -1, choices=['Percentile:100.0', 'Percentile:99.9'], style=wx.CB_READONLY)
        self.pctCB.Bind(wx.EVT_COMBOBOX, self.onChangePct)
        self.pctCB.SetSelection(0)
        hbox2.Add(self.pctCB, flag=flagsR, border=2)
        hbox2.AddSpacer(10)
        self.sycAdjustCB = wx.CheckBox(self, label = 'Synchronize Adjust') 
        self.sycAdjustCB.SetValue(True)
        self.sycAdjustCB.Bind(wx.EVT_CHECKBOX, self.onChangeSyn)
        hbox2.Add(self.sycAdjustCB, flag=flagsR, border=2)
        sizer.Add(hbox2, flag=flagsR, border=2)
        return sizer

#--distributionViewFrame-------------------------------------------------------
    def infoWinClose(self, event):
        """ Close the pop-up experiment setup window."""
        if self.infoWindow:
            self.infoWindow.Destroy()
            gv.iSetupPanel = None
            self.infoWindow = None
            self.updateLock = False    # continouse all the data load process

#--distributionViewFrame-------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        if (not self.updateLock) and time.time() - self.lastPeriodicTime >= gv.iUpdateRate:
            self.dataMgr.setPanelData('M')
            gv.iChartPanel0.updateDisplay()
            self.lastPeriodicTime = time.time()

#--distributionViewFrame-------------------------------------------------------
    def reloadData(self, event):
        """ Reload data from the data folder and update the display"""
        print("Reload data from the data folder. ")
        self.dataMgr.loadCSVData('D')
        gv.iChartPanel1.updateDisplay()

#--distributionViewFrame-------------------------------------------------------
    def onChangeDCT(self, event):
        """ Change the data display check data type."""
        self.dataMgr.setTypeChIdx(self.chartTypeCH1.GetSelection(), 'D')
        gv.iChartPanel1.updateDisplay()

#--distributionViewFrame-------------------------------------------------------
    def onChangeDMT(self, event):
        """ Change the model display data type."""
        self.dataMgr.setTypeChIdx(self.chartTypeCH0.GetSelection(), 'M')
        gv.iChartPanel0.updateDisplay()
        if self.synAdjust:
            self.chartTypeCH1.SetSelection(self.chartTypeCH0.GetSelection())
            self.onChangeDCT(None)

#--distributionViewFrame-------------------------------------------------------
    def onChangeLS(self, event):
        """ Change the line style. """
        gv.iLineStyle = self.lineStyleCB.GetSelection()+1
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

#--distributionViewFrame-------------------------------------------------------
    def onChangePct(self, event):
        """ Change the display data percentile."""
        setTag = self.pctCB.GetSelection()
        self.dataMgr.getDataPercentile(setTag)
        percentileVal = 1 if setTag == 0 else self.sampleCount*1.0/self.dataMgr.percentile
        gv.iChartPanel0.pixelScale = gv.iChartPanel1.pixelScale = percentileVal
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

#--distributionViewFrame-------------------------------------------------------
    def onChangeSR(self, event):
        """ change the sample rate of each data set."""
        self.dataMgr.sampleRate = (int(self.SampleRCH0.GetSelection())+1)*10
        self.dataMgr.setPanelData('M')
        self.dataMgr.setPanelData('D')
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

#--distributionViewFrame-------------------------------------------------------
    def onChangeSyn(self, evnet):
        """ Change the panel display Synchronize setting."""
        self.synAdjust = self.sycAdjustCB.GetValue()
        if self.synAdjust:
            self.chartTypeCH1.Enable(False)
            self.disModeDCB.Enable(False)
        else:
            self.chartTypeCH1.Enable(True)
            self.disModeDCB.Enable(True)

#--distributionViewFrame-------------------------------------------------------
    def onChangeUR(self, event):
        """ Change the update rate."""
        gv.iUpdateRate = self.updateRateCB.GetSelection()+1

#--distributionViewFrame-------------------------------------------------------
    def onChangeYS(self, event):
        """ Change the display Y-Axis Scale.(Logarithmic/linear)"""
        gv.iChartPanel0.displayMode = self.disModeMCB.GetSelection() 
        if self.synAdjust:
            self.disModeDCB.SetSelection(self.disModeMCB.GetSelection())
        gv.iChartPanel1.displayMode = self.disModeDCB.GetSelection() 
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

#--distributionViewFrame-------------------------------------------------------
    def onStartExp(self, mode):
        """ Run the experiment once."""
        print("Start the experiment.")        
        self.expThread.experimentStart()

#--distributionViewFrame-------------------------------------------------------
    def onSetupModelExp(self, event):
        """ Pop-up the model experiment setup window. """
        if self.infoWindow is None and gv.iSetupPanel is None:
            self.updateLock = True    # Lock all the data load process
            self.infoWindow = wx.MiniFrame(self, -1,
                                'NetFetcher [Model] Experiment Setup', 
                                pos=(300, 300), size=(620, 250),
                                style=wx.DEFAULT_FRAME_STYLE)
            gv.iSetupPanel = dvp.PanelSetting(self.infoWindow, 0)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

#--distributionViewFrame-------------------------------------------------------
    def onSetupCheckExp(self, event):
        """ Pop-up the check experiment setup window. """
        if self.infoWindow is None and gv.iSetupPanel is None:
            self.updateLock = True    # Lock all the data load process
            self.infoWindow = wx.MiniFrame(self, -1,
                                'NetFetcher [Check] Experiment Setup', 
                                pos=(300, 300), size=(620, 160),
                                style=wx.DEFAULT_FRAME_STYLE)
            gv.iSetupPanel = dvp.PanelSetting(self.infoWindow, 1)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionDataMgr(object):
    """ Manager module to process the csv files."""
    def __init__(self, parent):
        self.sampleRate = 30    # % of samples we will load from the [model] file.
        self.percentile = 1     # percentile of data we are going to show.     
        self.ModeChIdx = gv.iModelType
        self.DataChIdx = gv.iDataType
        self.modelD = []    # mode folder data set.
        self.dataD = []     # data folder data set.
        print("DistributionDataMgr: Loading data.")
        self.loadCSVData('M')   # load data from model folder.
        self.loadCSVData('D')   # load data from data folder.
        print("DistributionDataMgr: Set data for display.")
        self.setPanelData('M')
        self.setPanelData('D')
    
#--distributionDataMgr---------------------------------------------------------
    def getDataPercentile(self, setTag):
        """ Calculate the data pervertile value base on the input tag:
            0 - 100%, 1- 99.9%
        """
        self.percentile = 1 if setTag == 0 else np.percentile(self.dataD, 99.9)//1000

#--distributionDataMgr---------------------------------------------------------
    def loadCSVData(self, tag):
        """ Check all the csv file from the load the data. tag = 'M' : model folder
            tag ='D': data folder
        """
        if not tag:
            print("The input type tag must be defined!")
            return
        filePaths = None
        rowTypeIdx = 0 
        if tag == 'M':
            filePaths = glob.glob(gv.MODE_F_PATH)
            self.modelD = []
            gv.iChartPanel0.setLabel(filePaths)
            rowTypeIdx = self.ModeChIdx
        else:
            filePaths = glob.glob(gv.DATA_F_PATH)
            self.dataD = []
            gv.iChartPanel1.setLabel(filePaths)
            rowTypeIdx = self.DataChIdx
        for fileName in filePaths:
            dataSet = []
            with open(fileName) as f:
                f_csv = csv.reader(f)
                _ = next(f_csv)  # skip the csv header.
                for row in f_csv:
                    i = int(row[rowTypeIdx+1]) if rowTypeIdx < 5 else (int(row[3])+int(row[4]))
                    dataSet.append(i)
            if tag == 'M':
                self.modelD.append(dataSet)
            else:
                self.dataD.append(dataSet)

#--distributionDataMgr---------------------------------------------------------
    def setPanelData(self, tag):
        """ Set the data manager's data based on the smaple rate to panel for display. 
            tag = 'M' : model csv, tag ='D': data csv
        """
        displayPanel = gv.iChartPanel0 if tag == 'M' else gv.iChartPanel1
        dataList = self.modelD if tag == 'M' else self.dataD
        displayPanel.clearData()    # call the clearData to clear the panel record.
        for idx, dataSet in enumerate(dataList):
            for num in random.sample(dataSet, len(dataSet)*self.sampleRate//100):
                if num//1000 > SAMPLE_COUNT: continue  # filter the too big data.
                displayPanel.dataD[idx][num//1000] += 1

#--distributionDataMgr---------------------------------------------------------
    def setTypeChIdx(self, idx, tag):
        """ set the [model]/[data] type we are going to load and display."""
        if tag == 'M':
            if self.ModeChIdx == idx: return
            self.ModeChIdx = idx
        else:
            if self.DataChIdx == idx: return
            self.DataChIdx = idx
        self.loadCSVData(tag)
        self.setPanelData(tag)

#--distributionDataMgr---------------------------------------------------------
    def periodic(self, now):
        """ Call back every periodic time."""
        self.setPanelData('M') # load 

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyApp(wx.App):
    """ Init the frame and run the application"""
    def OnInit(self):
        mainFrame = distributionViewFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
