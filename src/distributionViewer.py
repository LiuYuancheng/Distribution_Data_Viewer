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

    def buildUISizer(self):
        """ Init the frame user interface and return the sizer."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        nb = wx.Notebook(self)
        ntbgPage1 = wx.Panel(nb)
        nb.AddPage(ntbgPage1, "Data display")
        hboxPg1= wx.BoxSizer(wx.VERTICAL)
        linechart1 = dvp.PanelChart(ntbgPage1, recNum=60)
        hboxPg1.Add(linechart1, flag=flagsR, border=2)
        hboxPg1.AddSpacer(5)
        hboxPg1.Add(wx.StaticLine(ntbgPage1, wx.ID_ANY, size=(1200, -1),
                                     style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        hboxPg1.AddSpacer(5)
        linechart2 = dvp.PanelChart(ntbgPage1, recNum=160)
        hboxPg1.Add(linechart2, flag=flagsR, border=2)
        self.pauseBt = wx.Button(ntbgPage1, label='Reload Data', style=wx.BU_LEFT, size=(80, 23))
        hboxPg1.Add(self.pauseBt, flag=flagsR, border=2)
        
        ntbgPage1.SetSizer(hboxPg1)

        #ntbgPage2 = wx.Panel(nb)

        ntbgPage2 = dvp.PanelMultInfo(nb)
        nb.AddPage(ntbgPage2, "Setting")
        sizer.Add(nb, 1, wx.EXPAND)
        return sizer

#-----------------------------------------------------------------------------
class MyApp(wx.App):
    """ Init the frame and run the application"""
    def OnInit(self):
        mainFrame = distributionViewFrame(None, -1, gv.APP_NAME)
        mainFrame.Show(True)
        return True
app = MyApp(0)
app.MainLoop()