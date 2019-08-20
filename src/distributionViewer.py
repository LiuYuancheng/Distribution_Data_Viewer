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

PERIODIC = 500      # update in every 500ms
SAMPLE_COUNT = 930  # 
DEF_SIZE = (1920, 750)
UPDATE_U = 0.5      # update time unit for test.

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
        self.infoWindow = None   # popup window to do the setting.
        self.loadLock = False
        # Creat the function menu bar.
        menubar = wx.MenuBar()
        menubar.Append(wx.Menu(), '&Help')
        self.SetMenuBar(menubar)
        
        #self.Bind(wx.EVT_MENU, self.onStartExp, startItem)
        # data type.
        self.displayChoice = \
            ('Type 0: Timestamping Delay',
             'Type 1: Preprocessing Delay',
             'Type 2: Disk Seek Delay',
             'Type 3: Disk Read Delay',
             'Type 4: Client Observed Delay',
             'Type 5: Input/Output Delay (Type 2 + Type 3)')
        # Init the UI
        self.SetSizer(self.buildUISizer())
        # The data manager.
        self.dataMgr = distributionDataMgr(self)
        # Init the periodic timer.
        self.lastPeriodicTime = time.time()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms
        # Show the frame.
        self.SetDoubleBuffered(True)
        self.Refresh(False)
        self.expThread = btcRun.commThread(1, "Thread-1", 1)

#-----------------------------------------------------------------------------
    def buildUISizer(self):
        """ Init the frame user interface and return the sizer."""
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        width, _ = wx.GetDisplaySize()
        appSize = (width, 700) if width == 1920 else (1600, 700)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Row index 0: model title, data type selection, simple rate selection.
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.Button(self, label='Data Source: [Model]', size=(
            140, 23)), flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        self.expMSBt = wx.Button(self, label='Setup', size=(60, 23))
        hbox0.Add(self.expMSBt, flag=flagsR, border=2)
        self.expMSBt.Bind(wx.EVT_BUTTON, self.onSetupModelExp)
        hbox0.AddSpacer(10)

        self.chartCH0 = wx.ComboBox(
            self, -1, choices=self.displayChoice, style=wx.CB_READONLY)
        self.chartCH0.Bind(wx.EVT_COMBOBOX, self.onMChoice)
        self.chartCH0.SetSelection(gv.iModelType)
        hbox0.Add(self.chartCH0, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        self.disModeMCB =  wx.ComboBox(
            self, -1, choices=['Logarithmic scale', 'Linear scale: Dynamic', 'Linear scale: Fixed'], style=wx.CB_READONLY)
        self.disModeMCB .SetSelection(0)
        self.disModeMCB.Bind(wx.EVT_COMBOBOX, self.onDisModeSelection)
        hbox0.Add(self.disModeMCB, flag=flagsR, border=2)
        sizer.Add(hbox0, flag=flagsR, border=2)
        # Row index 1: display panel for the model.
        gv.iChartPanel0 = linechart1 = dvp.PanelChart(
            self, 3, appSize=appSize, recNum=self.sampleCount)
        sizer.Add(linechart1, flag=flagsR, border=2)
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(width, -1),
                                style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        # Row index 2: model title, data type selection.
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.Button(self, label='Data Source: [Data]', size=(
            140, 23)), flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        
        self.expCSBt = wx.Button(self, label='Setup', size=(60, 23))
        hbox1.Add(self.expCSBt, flag=flagsR, border=2)
        self.expCSBt.Bind(wx.EVT_BUTTON, self.onSetupCheckExp)
        hbox1.AddSpacer(10)

        self.chartCH1 = wx.ComboBox(
            self, -1, choices=self.displayChoice, style=wx.CB_READONLY)
        self.chartCH1.Bind(wx.EVT_COMBOBOX, self.onDChoice)
        self.chartCH1.SetSelection(gv.iDataType)
        hbox1.Add(self.chartCH1, flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        self.disModeDCB =  wx.ComboBox(
            self, -1, choices=['Logarithmic scale', 'Linear scale: Dynamic', 'Linear scale: Fixed'], style=wx.CB_READONLY)
        self.disModeDCB .SetSelection(0)
        self.disModeDCB.Bind(wx.EVT_COMBOBOX, self.onDisModeSelection)
        hbox1.Add(self.disModeDCB, flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        self.pauseBt = wx.Button(
            self, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        self.pauseBt.Bind(wx.EVT_BUTTON, self.reloadData)
        hbox1.Add(self.pauseBt, flag=flagsR, border=2)
        sizer.Add(hbox1, flag=flagsR, border=2)
        # Row index 3: display panel for the model.
        gv.iChartPanel1 = linechart2 = dvp.PanelChart(
            self, 1, appSize=appSize, recNum=self.sampleCount)
        sizer.Add(linechart2, flag=flagsR, border=2)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(width, -1),
                                style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        # Row index 4: display setting
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
            self, -1, choices=['Sample Rate: '+str((i+1)*10) for i in range(10)], style=wx.CB_READONLY)
        self.SampleRCH0.Bind(wx.EVT_COMBOBOX, self.onChangeSR)
        self.SampleRCH0.SetSelection(2)
        hbox2.Add(self.SampleRCH0, flag=flagsR, border=2)
        sizer.Add(hbox2, flag=flagsR, border=2)

        hbox2.AddSpacer(10)
        self.pctCB = wx.ComboBox(
            self, -1, choices=['Percentile:100.0', 'Percentile:99.9'], style=wx.CB_READONLY)
        self.pctCB.Bind(wx.EVT_COMBOBOX, self.onChangePct)
        self.pctCB.SetSelection(0)
        hbox2.Add(self.pctCB, flag=flagsR, border=2)

        return sizer

#-----------------------------------------------------------------------------
    def infoWinClose(self, event):
        """ Close the pop-up detail information window"""
        if self.infoWindow:
            self.infoWindow.Destroy()
            gv.iSetupPanel = None
            self.infoWindow = None
            self.loadLock = False    # Lock all the data load process

#-----------------------------------------------------------------------------
    def reloadData(self, event):
        """ reload data from the data folder and update the display"""
        print("Reload data from the data folder. ")
        self.dataMgr.loadDataD()
        gv.iChartPanel1.updateDisplay()

#-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        if time.time() - self.lastPeriodicTime > gv.iUpdateRate*UPDATE_U:
            if not self.loadLock:
                self.dataMgr.setModelD()
            gv.iChartPanel0.updateDisplay()
            self.lastPeriodicTime = time.time()

#-----------------------------------------------------------------------------
    def onChangeSR(self, event):
        self.dataMgr.sampleRate= (int(self.SampleRCH0.GetSelection())+1)*10
        self.dataMgr.setModelD()
        self.dataMgr.setDataD()
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()
        #gv.iChartPanel0.sampleRate = (int(self.SampleRCH0.GetSelection())+1)*10
        #gv.iChartPanel1.sampleRate = (int(self.SampleRCH0.GetSelection())+1)*10

    def onChangeUR(self, event):
        """ Change the update rate."""
        gv.iUpdateRate = self.updateRateCB.GetSelection()+1

    def onChangeLS(self, event):
        """ Chnage the line style. """
        gv.iLineStyle = self.lineStyleCB.GetSelection()+1
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

#-----------------------------------------------------------------------------
    def onDChoice(self, event):
        """ Change the data display data type."""
        self.dataMgr.setDataChIdx(self.chartCH1.GetSelection())
        gv.iChartPanel1.updateDisplay()

#-----------------------------------------------------------------------------
    def onDisModeSelection(self, event):
        gv.iChartPanel0.displayMode = self.disModeMCB.GetSelection() 
        gv.iChartPanel1.displayMode = self.disModeDCB.GetSelection() 
        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

    def onChangePct(self, event):
        if self.pctCB.GetSelection() == 0:
            gv.iChartPanel0.pixelScale = 1
            gv.iChartPanel1.pixelScale = 1
        else:
            gv.iChartPanel0.pixelScale = self.sampleCount*1.0/self.dataMgr.percentile
            gv.iChartPanel1.pixelScale = self.sampleCount*1.0/self.dataMgr.percentile

        gv.iChartPanel0.updateDisplay()
        gv.iChartPanel1.updateDisplay()

#-----------------------------------------------------------------------------
    def onMChoice(self, event):
        """ Change the model display data type."""
        self.dataMgr.setModelChIdx(self.chartCH0.GetSelection())
        gv.iChartPanel0.updateDisplay()

    def onStartExp(self, mode):
        """ Run the experiment once."""
        print("Start the experiment.")        
        self.expThread.experimentStart()

#-----------------------------------------------------------------------------
    def onSetupModelExp(self, event):
        """ Pop-up the experiment setup window. """
        if self.infoWindow is None and gv.iSetupPanel is None:
            self.loadLock = True    # Lock all the data load process
            self.infoWindow = wx.MiniFrame(self, -1,
                                'NetFetcher [Model] Experiment Setup', 
                                pos=(300, 300), size=(620, 250),
                                style=wx.DEFAULT_FRAME_STYLE)
            gv.iSetupPanel = dvp.PanelSetting(self.infoWindow, 0)
            self.infoWindow.Bind(wx.EVT_CLOSE, self.infoWinClose)
            self.infoWindow.Show()

    def onSetupCheckExp(self, event):
        """ Pop-up the experiment setup window. """
        if self.infoWindow is None and gv.iSetupPanel is None:
            self.loadLock = True    # Lock all the data load process
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
        self.sampleRate = 30   # % of samples we will load from the [model] file.
        self.ModeChIdx = gv.iModelType
        self.DataChIdx = gv.iDataType
        print("DistributionDataMgr: Loading data.")
        self.modelD = []    # mode folder data set. 
        self.dataD  = []    # data folder data set.
        self.loadModelD()   # load data from model folder.
        self.loadDataD()    # load data from data folder.
        self.setModelD()
        self.setDataD()
        self.percentile = np.percentile(self.dataD, 99.9)//1000
        print("=============== %s" %str(self.percentile))

#-----------------------------------------------------------------------------
    def loadModelD(self):
        """ Check all the csv file from the model folder and load the data."""
        # clear the old display.
        self.modelD = []
        modelCSV = glob.glob(gv.MODE_F_PATH)
        #print("Distribution Mgr:    File in model folder to process: %s" %str(modelCSV))
        gv.iChartPanel0.setLabel(modelCSV)
        for fileName in modelCSV:
            #print(fileName)
            dataSet = []
            with open(fileName) as f:
                f_csv = csv.reader(f)
                _ = next(f_csv)  # skip the csv header.
                for row in f_csv:
                    i = int(row[self.ModeChIdx+1]) if self.ModeChIdx < 5 else (int(row[3])+int(row[4]))
                    dataSet.append(i)
            self.modelD.append(dataSet)

#-----------------------------------------------------------------------------
    def setModelD(self):
        """ Set the model data."""
        gv.iChartPanel0.clearData()
        for idx, dataSet in enumerate(self.modelD):
            for num in random.sample(dataSet, len(dataSet)*self.sampleRate//100):
                if num//1000 > SAMPLE_COUNT: continue  # filter the too big data.
                gv.iChartPanel0.dataD[idx][num//1000] += 1

    def setDataD(self):
        """ Set the model data."""
        gv.iChartPanel1.clearData()
        for idx, dataSet in enumerate(self.dataD):
            for num in random.sample(dataSet, len(dataSet)*self.sampleRate//100):
                if num//1000 > SAMPLE_COUNT: continue  # filter the too big data.
                gv.iChartPanel1.dataD[idx][num//1000] += 1

#-----------------------------------------------------------------------------
    def loadDataD(self):
        """ Check all the csv file from the data folder and load the data."""
        self.dataD = [] 
        modelCSV = glob.glob(gv.DATA_F_PATH)
        gv.iChartPanel1.setLabel(modelCSV)
        for fileName in modelCSV:
            #print(fileName)
            dataSet = []
            with open(fileName) as f:
                f_csv = csv.reader(f)
                _ = next(f_csv) # skip the csv header.
                for row in f_csv:
                    i = int(row[self.DataChIdx+1]) if self.DataChIdx < 5 else (int(row[3])+int(row[4]))
                    dataSet.append(i)
            self.dataD.append(dataSet)


#-----------------------------------------------------------------------------
    def setDataChIdx(self, idx):
        """ set the [data] type we are going to load and display."""
        if self.DataChIdx == idx: return
        print(idx)
        self.DataChIdx = idx
        self.loadDataD()
        self.setDataD()

#-----------------------------------------------------------------------------
    def setModelChIdx(self, idx):
        """ set the [model] type we are going to load and display."""
        if self.ModeChIdx == idx: return
        self.ModeChIdx = idx
        self.loadModelD()
        self.setModelD()

#-----------------------------------------------------------------------------
    def periodic(self, now):
        """ Call back every periodic time."""
        self.loadModelD() # load 

#-----------------------------------------------------------------------------
class MyApp(wx.App):
    """ Init the frame and run the application"""
    def OnInit(self):
        mainFrame = distributionViewFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
