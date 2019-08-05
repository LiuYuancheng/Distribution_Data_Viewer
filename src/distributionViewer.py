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
import wx # use wx to build the UI.
# Auto adjust App size

import distributionViewGlobal as gv
import distributionViewPanel as dvp

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionViewFrame(wx.Frame):
    """ Main frame of the distribution viewer."""
    def __init__(self, parent, id, title):
        """ Init the UI and all parameters """
        wx.Frame.__init__(self, parent, id, title, size=(1600, 650))
        #self.SetIcon(wx.Icon(gv.ICON_PATH))
        self.sampleCount = 860
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
        self.chartCH0.SetSelection(4)
        hbox0.Add(self.chartCH0, flag=flagsR, border=2)
        sizer.Add(hbox0, flag=flagsR, border=2)
        # Row index 1: the display channel.
        gv.iChartPanel0 = linechart1 = dvp.PanelChart(
            self, 3,appSize=appSize, recNum=self.sampleCount)
        sizer.Add(linechart1, flag=flagsR, border=2)
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(1200, -1),
                                  style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        gv.iChartPanel1 = linechart2 = dvp.PanelChart(
            self, 1,appSize=appSize, recNum=self.sampleCount)
        sizer.Add(linechart2, flag=flagsR, border=2)
        self.pauseBt = wx.Button(
            self, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        sizer.Add(self.pauseBt, flag=flagsR, border=2)
        return sizer

    def OnSetup(self, event):
        print("User clicked.")


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionDataMgr(object):
    """ distritutionDataMgr to process the csv files.
    """
    def __init__(self, parent):
        """ Init all the element on the map. All the parameters are public to other 
            module.
        """ 
        # read the module files: 
        with open(gv.MODE_F_PATH) as f:
            f_csv = csv.reader(f)
            _ = next(f_csv) # skip the csv header.
            for row in f_csv:
                idx = (int(row[3])+int(row[4]))//1000
                if idx > 750: continue # filter the too big data.
                gv.iChartPanel0.dataD[0][idx] += 1              
        # print(gv.iChartPanel0.dataD)

        # read the data files:
        with open(gv.DATA_F_PATH) as f:
            f_csv = csv.reader(f)
            _ = next(f_csv)
            for row in f_csv:
                data = (int(row[3])+int(row[4]))//1000
                if data > 750: continue
                gv.iChartPanel1.dataD[0][data] += 1
        # print(gv.iChartPanel1.dataD)





#-----------------------------------------------------------------------------
class MyApp(wx.App):
    """ Init the frame and run the application"""
    def OnInit(self):
        mainFrame = distributionViewFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
