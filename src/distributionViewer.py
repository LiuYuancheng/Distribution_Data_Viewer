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
import distributionViewGlobal as gv
import distributionViewPanel as dvp

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class distributionViewFrame(wx.Frame):
    """ Main frame of the distribution viewer."""
    def __init__(self, parent, id, title):
        """ Init the UI and all parameters """
        wx.Frame.__init__(self, parent, id, title, size=(1200, 700))
        #self.SetIcon(wx.Icon(gv.ICON_PATH))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.SetSizer(self.buildUISizer())
        # The data manager.
        self.dataMgr = distributionDataMgr(self)
        gv.iChartPanel0.colorIdx = 0
        gv.iChartPanel1.colorIdx = 1
#-----------------------------------------------------------------------------
    def buildUISizer(self):
        """ Init the frame user interface and return the sizer."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        nb = wx.Notebook(self)
        # Page 1: data distribution graph.
        ntbgPage1 = wx.Panel(nb)
        nb.AddPage(ntbgPage1, "Data Display")
        hboxPg1 = wx.BoxSizer(wx.VERTICAL)
        gv.iChartPanel0 = linechart1 = dvp.PanelChart(ntbgPage1, recNum=760)
        hboxPg1.Add(linechart1, flag=flagsR, border=2)
        hboxPg1.AddSpacer(5)
        hboxPg1.Add(wx.StaticLine(ntbgPage1, wx.ID_ANY, size=(1200, -1),
                                  style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hboxPg1.AddSpacer(5)
        gv.iChartPanel1 = linechart2 = dvp.PanelChart(ntbgPage1, recNum=760)
        hboxPg1.Add(linechart2, flag=flagsR, border=2)
        self.pauseBt = wx.Button(
            ntbgPage1, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        hboxPg1.Add(self.pauseBt, flag=flagsR, border=2)
        ntbgPage1.SetSizer(hboxPg1)
        # Page 2 : program setting
        ntbgPage2 = dvp.PanelSetting(nb)
        nb.AddPage(ntbgPage2, "Setting")
        sizer.Add(nb, 1, wx.EXPAND)
        return sizer

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
                gv.iChartPanel0.dataD[idx] += 1              
        # print(gv.iChartPanel0.dataD)

        # read the data files:
        with open(gv.DATA_F_PATH) as f:
            f_csv = csv.reader(f)
            _ = next(f_csv)
            for row in f_csv:
                data = (int(row[3])+int(row[4]))//1000
                if data > 750: continue
                gv.iChartPanel1.dataD[data] += 1
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
