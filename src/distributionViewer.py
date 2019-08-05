#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        distributionView.py
#
# Purpose:     This module is used to read the data from serveral CSV file and 
#              draw the distribution diagram.
#             
# Author:      Yuancheng Liu
#
# Created:     2019/08/02
# Copyright:   NUS-Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import io, sys
import csv
import time
import glob
import wx # use wx to build the UI.
# Auto adjust App size
import random


import distributionViewGlobal as gv
import distributionViewPanel as dvp

PERIODIC = 500
SAMPLE_COUNT = 860
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionViewFrame(wx.Frame):
    """ Main frame of the distribution viewer."""
    def __init__(self, parent, id, title):
        """ Init the UI and all parameters """
        wx.Frame.__init__(self, parent, id, title, size=(1600, 720))
        #self.SetIcon(wx.Icon(gv.ICON_PATH))
        self.sampleCount = SAMPLE_COUNT
        self.infoWindow= None
        # Creat the menu bar.
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_NEW, 'Setup', 'Setup application')
        menubar.Append(fileMenu, '&Experiment')
        menubar.Append(wx.Menu(), '&DataDisplay')
        menubar.Append(wx.Menu(), '&Help')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnSetup, fileItem)

        self.displayChoice = \
            ('Type 0: Timestamping Delay', 
            'Type 1: Preprocessing Delay',
            'Type 2: Disk Seek Delay',
            'Type 3: Disk Read Delay', 
            'Type 4: Client Observed Delay',
            'Type 5: Input/Output Delay (Type 2 + Type 3)')

        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetSizer(self.buildUISizer())
        # The data manager.
        self.dataMgr = distributionDataMgr(self)
        gv.iChartPanel0.colorIdx = 0
        gv.iChartPanel1.colorIdx = 1


        self.lastPeriodicTime = time.time() 
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.timer.Start(PERIODIC)  # every 500 ms

        self.SetDoubleBuffered(True)

        #self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Refresh(False)

#-----------------------------------------------------------------------------
    def buildUISizer(self):
        """ Init the frame user interface and return the sizer."""

        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        width, _ = wx.GetDisplaySize()
        print(width)
        appSize = (width, 700) if width == 1920 else (1600, 700)

        sizer = wx.BoxSizer(wx.VERTICAL)
        # Row index 0: title and data selection
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(wx.Button(self, label='Data Source: [Model]', size=(140, 23)), flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        self.chartCH0 = wx.ComboBox(self, -1, choices=self.displayChoice, style=wx.CB_READONLY)
        self.chartCH0.Bind(wx.EVT_COMBOBOX, self.onMChoice)
        self.chartCH0.SetSelection(4)
        hbox0.Add(self.chartCH0, flag=flagsR, border=2)
        hbox0.AddSpacer(10)
        self.SampleRCH0 = wx.ComboBox(self, -1, choices= ['Sample Rate: '+str((i+1)*10) for i in range(10)], style=wx.CB_READONLY)
        self.SampleRCH0.SetSelection(4)
        hbox0.Add(self.SampleRCH0, flag=flagsR, border=2)
        sizer.Add(hbox0, flag=flagsR, border=2)
        # Row index 1: the display channel.
        gv.iChartPanel0 = linechart1 = dvp.PanelChart(
            self, 3, appSize=appSize, recNum=self.sampleCount)
        sizer.Add(linechart1, flag=flagsR, border=2)
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(width, -1),
                                  style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        # Row index 2: 
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.Button(self, label='Data Source: [Data]', size=(140, 23)), flag=flagsR, border=2)
        hbox1.AddSpacer(10)
        self.chartCH1 = wx.ComboBox(self, -1, choices=self.displayChoice, style=wx.CB_READONLY)
        self.chartCH1.Bind(wx.EVT_COMBOBOX, self.onDChoice)
        self.chartCH1.SetSelection(4)
        hbox1.Add(self.chartCH1, flag=flagsR, border=2)
        self.pauseBt = wx.Button(
            self, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        hbox1.AddSpacer(10)
        hbox1.Add(self.pauseBt, flag=flagsR, border=2)
        sizer.Add(hbox1, flag=flagsR, border=2)
        # Row index 3:
        gv.iChartPanel1 = linechart2 = dvp.PanelChart(
            self, 1,appSize=appSize, recNum=self.sampleCount)
        sizer.Add(linechart2, flag=flagsR, border=2)        
        return sizer

    def periodic(self, event):
        """ Call back every periodic time."""
        pass
        # Set the title of the frame.
        #self.SetTitle( ' '.join((gv.APP_NAME, datetime.now().strftime("[ %m/%d/%Y, %H:%M:%S ]"))))
        #if gv.iEmgStop: return
        #timeStr = time.time()
        #self.mapPanel.periodic(timeStr)
        if time.time() - self.lastPeriodicTime > 3:
            self.dataMgr.loadModelD()
            gv.iChartPanel0.updateDisplay()
            self.lastPeriodicTime = time.time()

    def OnSetup(self, event):
        print("User clicked.")

    def onMChoice(self, event):
        self.dataMgr.setModelChIdx(self.chartCH0.GetSelection())
        gv.iChartPanel0.updateDisplay()

    def onDChoice(self, event):
        self.dataMgr.setDataChIdx(self.chartCH1.GetSelection())
        gv.iChartPanel1.updateDisplay()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionDataMgr(object):
    """ distritutionDataMgr to process the csv files.
    """
    def __init__(self, parent):
        """ Init all the element on the map. All the parameters are public to other 
            module.
        """ 
        self.sampleRate = 100
        self.ModeChIdx = 4
        self.DataChIdx = 4
        self.loadModelD()
        self.loadDataD()
        # print(gv.iChartPanel1.dataD)

    def setModelChIdx(self, idx):
        if self.ModeChIdx == idx: return
        self.ModeChIdx = idx
        gv.iChartPanel0.clearData()
        self.loadModelD()

    def setDataChIdx(self, idx):
        if self.DataChIdx == idx: return
        print(idx)
        self.DataChIdx = idx
        
        self.loadDataD()

    def loadModelD(self):
        # Check Model folder
        gv.iChartPanel0.clearData()
        modelCSV = glob.glob(gv.MODE_F_PATH)
        print("Distribution Mgr: File in model folder to process: %s" %str(modelCSV))
        for idx, fileName in enumerate(modelCSV):
            print(fileName)
            with open(fileName) as f:
                f_csv = csv.reader(f)
                _ = next(f_csv) # skip the csv header.
                for rIdx, row in enumerate(f_csv):
                    if random.randint(0, 1000) > self.sampleRate:
                        continue
                    i = int(row[self.ModeChIdx+1]) if self.ModeChIdx < 5 else (int(row[3])+int(row[4]))
                    if i//1000 > SAMPLE_COUNT: continue # filter the too big data.
                    gv.iChartPanel0.dataD[idx][i//1000] += 1

    def loadDataD(self):
        gv.iChartPanel1.clearData()
        modelCSV = glob.glob(gv.DATA_F_PATH)
        for idx, fileName in enumerate(modelCSV):
            print(fileName)
            with open(fileName) as f:
                f_csv = csv.reader(f)
                _ = next(f_csv)
                for row in f_csv:
                    i = int(row[self.DataChIdx+1]) if self.DataChIdx < 5 else (int(row[3])+int(row[4]))
                    if i//1000 > SAMPLE_COUNT: continue
                    gv.iChartPanel1.dataD[idx][i//1000] += 1


    def periodic(self, now):
        self.loadModelD()


#-----------------------------------------------------------------------------
class MyApp(wx.App):
    """ Init the frame and run the application"""
    def OnInit(self):
        mainFrame = distributionViewFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
