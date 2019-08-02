#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        distributionView.py
#
# Purpose:     This module is used to read the data from XAKA people counting
#              sensor and show the data in the user interface.(sucfunctions: 
#              register the sensor to the server, automaticall detect the sensor)
#             
# Author:      Yuancheng Liu
#
# Created:     2019/08/02
# Copyright:   NUS – Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import io, sys
import csv
import platform
import glob
import wx # use wx to build the UI.
import time
import serial
import threading
import random
import distributionViewGlobal as gv
import distributionViewPanel as dvp

class distributionViewFrame(wx.Frame):
    """ XAKA people counting sensor reader with sensor registration function. """
    def __init__(self, parent, id, title):
        """ Init the UI and all parameters """
        wx.Frame.__init__(self, parent, id, title, size=(1200, 700))
        #self.SetIcon(wx.Icon(gv.ICON_PATH))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))

        # Init the UI.
        self.SetSizer(self.buildUISizer())
        self.mgr = distributionDataMgr(self)


    def buildUISizer(self):
        """ Init the frame user interface and return the sizer."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        nb = wx.Notebook(self)
        ntbgPage1 = wx.Panel(nb)
        nb.AddPage(ntbgPage1, "Data display")
        hboxPg1= wx.BoxSizer(wx.VERTICAL)
        linechart1 = dvp.PanelChart(ntbgPage1, recNum=60)
        gv.iChartPanel0 = linechart1
        hboxPg1.Add(linechart1, flag=flagsR, border=2)
        hboxPg1.AddSpacer(5)
        hboxPg1.Add(wx.StaticLine(ntbgPage1, wx.ID_ANY, size=(1200, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hboxPg1.AddSpacer(5)
        linechart2 = dvp.PanelChart(ntbgPage1, recNum=160)
        gv.iChartPanel1 = linechart2
        hboxPg1.Add(linechart2, flag=flagsR, border=2)
        self.pauseBt = wx.Button(ntbgPage1, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        hboxPg1.Add(self.pauseBt, flag=flagsR, border=2)
        
        ntbgPage1.SetSizer(hboxPg1)

        #ntbgPage2 = wx.Panel(nb)

        ntbgPage2 = dvp.PanelMultInfo(nb)
        nb.AddPage(ntbgPage2, "Setting")
        sizer.Add(nb, 1, wx.EXPAND)
        return sizer


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
            header = next(f_csv)
            for row in f_csv:
                #print((row[3],row[4]))
                data = (int(row[3])+int(row[4]))//1000
                if data > 750: 
                    #print(data)
                    continue
                gv.iChartPanel0.dataD[data] += 1
                gv.iChartPanel0.color = 0
        print(gv.iChartPanel0.dataD)
        print("--")
        # read the data files:
        with open(gv.MODE_F_PATH) as f:
            f_csv = csv.reader(f)
            header = next(f_csv)
            for row in f_csv:
                #print((row[3],row[4]))
                data = (int(row[3])+int(row[4]))//1000
                if data > 750: 
                    #print(data)
                    continue
                gv.iChartPanel1.dataD[data] += 1
                gv.iChartPanel1.color = 1

        print(gv.iChartPanel1.dataD)

#-----------------------------------------------------------------------------
class MyApp(wx.App):
    """ Init the frame and run the application"""
    def OnInit(self):
        mainFrame = distributionViewFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True
app = MyApp(0)
app.MainLoop()