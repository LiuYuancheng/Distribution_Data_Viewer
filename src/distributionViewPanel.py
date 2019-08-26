
#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        distributionViewPanel.py
#
# Purpose:     This module is used to provide different function panels for the 
#              distributionViewer. 
#              
# Author:      Yuancheng Liu
#
# Created:     2019/08/02
# Copyright:   NUS-Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import wx
import random
import wx.grid
import distributionViewGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelChart(wx.Panel):
    """ This function is used to provide lineChart wxPanel to show the all the 
        data as distribution lines.
    """
    def __init__(self, parent, dataSetNum, appSize=(1600, 290), recNum=750):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=appSize)
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.recNum = recNum    # how many delay samples will be show on one chart.
        self.appSize = appSize  # the panel size.
        self.updateFlag = True  # flag whether we update the diaplay area
        self.dataSetNum = dataSetNum    # how many charts.
        self.dataD = [[0]*recNum for _ in range(dataSetNum)]
        self.textFont = None    # Panel text font.
        # Above line can not use [[0]*num]*num, otherwise change one element 
        # all column will be change, the explaination is here: 
        # https://stackoverflow.com/questions/2739552/2d-list-has-weird-behavor-when-trying-to-modify-a-single-value
        self.times = [n for n in range(self.recNum//10)]  # X-Axis(time delay).
        self.maxCount = 0       # max count of the delay in the current data set.
        self.percentileScale = 1     # how many pixel scale will extend for x-Axis. 
        self.compareOverlay = False # Overlay the compare data.(compare data save in <self.dataD[-1]>)
        self.displayMode = 0 # 0 - Logarithmic scale, 1 - linear scale real, 2-linear scale fix
        self.logScale = (10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000)
        self.logScaleShow = (1, 0, 1, 0, 0, 1, 0, 0, 1, 0) # 0 - hide, 1- show.
        self.labelInfo = ['Data1', 'Data2', 'Data3', 'exp-data[compare]']
        self.Bind(wx.EVT_PAINT, self.onPaint)

#--PanelChart------------------------------------------------------------------     
    def _buildSplinePtList(self, data, idx):
        """ build the spline pixel points list based on the display mode."""
        recNum, deltY = int(self.recNum*1.0/self.percentileScale), self.appSize[1]//200
        if self.displayMode == 0:
            return [(int(i*self.percentileScale+idx)*2, self._scaleCvrt(data[i])) for i in range(recNum)]
        elif self.displayMode == 1:
            return [(int(i*self.percentileScale+idx)*2, int(data[i])*200*deltY//self.maxCount) for i in range(recNum)]
        elif self.displayMode == 2:
            return [(int(i*self.percentileScale+idx)*2, min(200*deltY, int(data[i])*deltY)) for i in range(recNum)]

#--PanelChart------------------------------------------------------------------      
    def clearData(self):
        """ Clear all the times data to 0."""
        self.dataD = [[0]*self.recNum for _ in range(self.dataSetNum)]

#--PanelChart------------------------------------------------------------------ 
    def _drawBG(self, dc):
        """ Draw the line chart background."""
        x, y = self.appSize
        dc.SetPen(wx.Pen('WHITE'))
        dc.DrawRectangle(1, 1, x, y-90)
        dc.DrawText('NetFetcher Delay Time Distribution', 2, y-45)
        dc.DrawText('Occurences', -35, y-75)
        dc.DrawText('Delay[ microseconds ]', 700, -25)
        # Draw Axis and Grids:(Y:delay time, X:occurences)
        dc.SetPen(wx.Pen('#D5D5D5'))  # dc.SetPen(wx.Pen('#0AB1FF'))
        # Draw the Y-Axis
        dc.DrawLine(1, 1, 1, y)
        deltY = y//200*20 # <- don't replace by y//100*10 or y//10
        for i in range(1,11):
            dc.DrawLine(-5, i*deltY, x, i*deltY)  # Y-Grid
            if self.displayMode == 0:  # Logarithmic scale Y-Axis
                scaleIdx = i-1
                if self.logScaleShow[scaleIdx]:
                    # format to ## int, such as 02
                    dc.DrawText(str(self.logScale[scaleIdx]), -30, i*deltY+5)
            else:   # Linear scale Y-Axis
                ylabel = str(self.maxCount//10 *i) if self.displayMode == 1 else str(i*20).zfill(3)
                # format to ## int, such as 02
                dc.DrawText(ylabel, -30, i*deltY+5)
        # Draw the X-Axis
        dc.DrawLine(1, 1, x, 1)
        pixelU = int(20*self.percentileScale)
        for i in range(len(self.times)):
            dc.DrawLine(i*pixelU, -5, i*pixelU, deltY*10)  # X-Grid
            dc.DrawText(str(self.times[i]).zfill(2), i*pixelU-5, -5)

#--PanelChart--------------------------------------------------------------------
    def _drawFG(self, dc):
        """ Draw the front ground data distribution chart line."""
        item = ((self.labelInfo[0], 'RED'), 
                (self.labelInfo[1], '#529955'), 
                (self.labelInfo[2], 'BLUE'),
                (self.labelInfo[3], 'BLACK')
                )
        # Draw the charts.
        y = self.appSize[1] - 75
        for idx, data in enumerate(self.dataD):
            (label, color) = item[idx] if self.dataSetNum != 1 else item[-1]
            # Draw the line sample.
            dc.SetPen(wx.Pen(color, width=gv.iLineStyle, style=wx.PENSTYLE_SOLID))
            dc.SetBrush(wx.Brush(color))
            dc.DrawText(label, idx*200+150, y+10)
            dc.DrawRectangle(120+idx*200, y, 20, 6)
            if self.dataSetNum != 1 and  idx < self.dataSetNum -1:
                dc.DrawSpline(self._buildSplinePtList(data, idx)) # slightly shift idx.
            elif self.compareOverlay or self.dataSetNum == 1:
                dc.SetPen(wx.Pen(wx.Colour((210, 210, 210)),
                                 width=2, style=wx.PENSTYLE_SOLID))
                gdc = wx.GCDC(dc)
                r, g, b, alph = 120, 120, 120, 128  # half transparent alph
                gdc.SetBrush(wx.Brush(wx.Colour(r, g, b, alph)))
                gdc.DrawPolygon(self._buildSplinePtList(data, 0)) # not slightly shift.

#--PanelChart------------------------------------------------------------------  
    def _scaleCvrt(self, n):
        """ Convert the data from liner scale Y-axis to Logarithmic scale Y-axis."""
        deltY = self.appSize[1]//200*20
        for idx, val in enumerate(self.logScale):
            if n <= val:
                # Get the previous scale.
                preVal = 0 if idx == 0 else self.logScale[idx-1]
                # Compare with the pervious scale calculate the delta-pixel distance.
                return int((n-preVal)/float((val-preVal))*deltY+deltY*(idx))
        return deltY*10  # return the max

#--PanelChart------------------------------------------------------------------ 
    def onPaint(self, event):
        """ Main panel drawing function."""
        dc = wx.PaintDC(self)
        # set the axis orientation area and fmt to up + right direction.
        dc.SetDeviceOrigin(40, self.appSize[1]-40)
        dc.SetAxisOrientation(True, True)
        # set the text font
        if self.textFont is None:
            self.textFont  = dc.GetFont()
            self.textFont.SetPointSize(8)
        dc.SetFont(self.textFont)
        # Calculate the Y-up max limit value if under linear dynamic mode.
        self.maxCount = max([max(i) for i in self.dataD]) if self.displayMode == 1 else 0
        # draw the background 
        self._drawBG(dc)
        # draw the distribution chart.
        self._drawFG(dc)

#--PanelChart------------------------------------------------------------------ 
    def periodic(self, event):
        """ Call back every periodic time."""
        pass

#--PanelChart------------------------------------------------------------------  
    def setLabel(self, labelList):
        """ Set the chart color label. <labelList>: the list of the CSV file's path."""
        splitChr = '\\' if gv.WINP else '/'
        for i in range(len(labelList)):
            self.labelInfo[i] = str(labelList[i].split(splitChr)[-1])[:-3]

#--PanelChart------------------------------------------------------------------ 
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function 
            will set the self update flag.
        """
        if updateFlag is None and self.updateFlag: 
            self.Refresh(False)
            self.Update()
        else:
            self.updateFlag = updateFlag

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelSetting(wx.Panel):
    """ Experiment setup panel. Create the experiment running *.bat file based
        on the users's filled in data and call the experiment run program.
    """
    def __init__(self, parent, mode):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(620, 250))
        self.mode = mode
        self.SetBackgroundColour(wx.Colour(200, 200, 210))
        self.SetSizer(self.buidUISizer())

#--PanelSetting----------------------------------------------------------------
    def buidUISizer(self):
        """ Build the Panel UI"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        flagsR = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticText(
            self, label="Fill The Information In The Grid: "), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(640, -1),
                                style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        self.grid = wx.grid.Grid(self, -1)
        collumNum = 5 if self.mode == 0 else 1
        self.grid.CreateGrid(collumNum, 6)
        # Set the Grid size.
        self.grid.SetRowLabelSize(40)
        self.grid.SetColSize(0, 80)
        self.grid.SetColSize(1, 80)
        self.grid.SetColSize(2, 80)
        self.grid.SetColSize(3, 80)
        self.grid.SetColSize(4, 80)
        self.grid.SetColSize(5, 150)
        # Set the Grid's labels.
        self.grid.SetColLabelValue(0, 'IP Address')
        self.grid.SetColLabelValue(1, 'Port Num ')
        self.grid.SetColLabelValue(2, 'File ID ')
        self.grid.SetColLabelValue(3, 'Block Num')
        self.grid.SetColLabelValue(4, 'Iterations ')
        self.grid.SetColLabelValue(5, 'Output File')
        #self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.highLightMap)
        sizer.Add(self.grid, flag=flagsR, border=2)
        sizer.AddSpacer(5)
        # Add the experiment bat file generation button.
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.pauseBt = wx.Button(
            self, label='Calibration', style=wx.BU_LEFT, size=(100, 23))
        self.pauseBt.Bind(wx.EVT_BUTTON, self.onConstruct)
        hbox.Add(self.pauseBt, flag=flagsR, border=2)
        hbox.AddSpacer(10)
        hbox.Add(wx.StaticText(self, label="--->"), flag=flagsR, border=2)
        hbox.AddSpacer(10)
        self.fetchBt = wx.Button(
            self, label='BatchRun', style=wx.BU_LEFT, size=(100, 23))
        self.fetchBt.Bind(wx.EVT_BUTTON, self.onStartExp)
        hbox.Add(self.fetchBt, flag=flagsR, border=2)
        self.fetchBt.Enable(False)
        sizer.Add(hbox, flag=flagsR, border=2)
        return sizer

#--PanelSetting----------------------------------------------------------------
    def onStartExp(self, event):
        """ Start the experiment."""
        gv.iMainFame.onStartExp(self.mode)

#--PanelSetting----------------------------------------------------------------
    def onConstruct(self, event):
        """ Create the experiment setup file based on data in the grid. """
        with open(gv.CONFIG_FILE[self.mode], 'w') as fh:
            collumNum = 5 if self.mode == 0 else 1
            for i in range(collumNum):
                if self.grid.GetCellValue(i, 0) == '':continue
                data = [self.grid.GetCellValue(i, j) for j in range(6)]
                line = 'Run: '+data[0]+':'+data[1]+' ' + \
                    data[2]+':'+data[3]+' '+data[4]+' '+data[5]+'\n'
                fh.write(line)
                fh.write('sleep1\n\n')
        self.fetchBt.Enable(True)
