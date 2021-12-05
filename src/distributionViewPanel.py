
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
import time
import wx.grid
import distributionViewGlobal as gv

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelChart(wx.Panel):
    """ This function is used to provide lineChart wxPanel to show the input
        sample data as distribution lines.
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
        self.shiftOffset = 0    # number of shift on the x-Axis.
        # Above line can not use [[0]*num]*num, otherwise change one element 
        # all column will be change, the explaination is here: 
        # https://stackoverflow.com/questions/2739552/2d-list-has-weird-behavor-when-trying-to-modify-a-single-value
        self.times = [n for n in range(self.recNum//10)]  # X-Axis(time delay).
        self.maxCount = 0       # max count of the delay in the current data set.
        self.percentileScale = 1    # how many pixel scale will extend for x-Axis. 
        self.compareOverlay = False # Overlay the compare data.(compare data save in <self.dataD[-1]> )
        self.displayMode = 0        # 0 - Logarithmic scale, 1 - linear scale real, 2-linear scale fix
        self.logScale = (10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000)
        self.logScaleShow = (1, 0, 1, 0, 0, 1, 0, 0, 1, 0) # 0 - hide, 1- show.
        self.labelInfo = ['Data1', 'Data2', 'Data3', 'exp-data[compare]']
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.SetDoubleBuffered(True)

#--PanelChart------------------------------------------------------------------     
    def _buildSplinePtList(self, data, idx):
        """ build the spline pixel points list based on the display mode."""
        recNum, deltY = int(self.recNum*1.0/self.percentileScale), self.appSize[1]//200
        if self.displayMode == 0:
            return [(int(i*self.percentileScale*1.5)+idx, self._scaleCvrt(data[i])) for i in range(recNum)]
        elif self.displayMode == 1:
            return [(int(i*self.percentileScale*1.5)+idx, int(data[i])*200*deltY//self.maxCount) for i in range(recNum)]
        elif self.displayMode == 2:
            return [(int(i*self.percentileScale*1.5)+idx, min(200*deltY, int(data[i])*deltY)) for i in range(recNum)]

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
        deltY = int((y-90)//10)  # <- don't replace by y//100*10 or y//10
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
        pixelU = int(15*self.percentileScale)
        for i in range(len(self.times)):
            dc.DrawLine(i*pixelU, -5, i*pixelU, deltY*10)  # X-Grid
            if i % 5 == 0: 
                dc.DrawText(str(self.times[i]+self.shiftOffset).zfill(2), i*pixelU-5, -5)

#--PanelChart--------------------------------------------------------------------
    def _drawFG(self, dc):
        """ Draw the front ground data distribution chart line."""
        colorSet, y = ((200, 0, 0), (82, 153, 85), (0, 0, 200),
                       (120, 120, 120)), self.appSize[1] - 75 
        # Draw the label.
        for idx, label in enumerate(self.labelInfo):
            color = colorSet[idx]
            dc.SetPen(wx.Pen(color, width=gv.iLineStyle, style=wx.PENSTYLE_SOLID))
            dc.SetBrush(wx.Brush(wx.Colour(color)))
            dc.DrawText(label, idx*200+150, y+10)
            dc.DrawRectangle(120+idx*200, y, 20, 6)
        gdc = wx.GCDC(dc) if gv.iLineStyle == 3 else None # can only have one gdc.
        # Draw the charts.
        for idx, data in enumerate(self.dataD):
            color = colorSet[idx] if self.dataSetNum != 1 else colorSet[-1]
            dc.SetPen(wx.Pen(color, width=gv.iLineStyle, style=wx.PENSTYLE_SOLID))
            # Draw the line sample.
            if self.dataSetNum != 1 and idx < self.dataSetNum -1:
                if gv.iLineStyle != 3:
                    dc.DrawSpline(self._buildSplinePtList(data, idx)) # slightly shift idx.
                else:
                    (r, g, b),  alph = color, 128 # half transparent alph
                    gdc.SetBrush(wx.Brush(wx.Colour(r, g, b, alph)))
                    gdc.DrawPolygon(self._buildSplinePtList(data, idx))
            elif self.compareOverlay or self.dataSetNum == 1:
                dc.SetPen(wx.Pen(wx.Colour((210, 210, 210)),
                                 width=2, style=wx.PENSTYLE_SOLID))
                if gdc is None: gdc = wx.GCDC(dc)
                r, g, b, alph = 120, 120, 120, 128  # half transparent alph
                gdc.SetBrush(wx.Brush(wx.Colour(r, g, b, alph)))
                gdc.DrawPolygon(self._buildSplinePtList(data, 0)) # not slightly shift.

#--PanelChart------------------------------------------------------------------  
    def _scaleCvrt(self, n):
        """ Convert the data from liner scale Y-axis to Logarithmic scale Y-axis."""
        deltY = (self.appSize[1]-90)//10
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
        splitChr = '\\' #if gv.WINP else '/'
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
        self.SetSizer(self._buidUISizer())
        self.setCellVals()

#--PanelSetting----------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the Panel UI"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        flagsR = wx.RIGHT  # wx.ALIGN_CENTER_VERTICAL
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
        self.processDisplay = wx.Gauge(self, range=10, size=(350, 22), style=wx.GA_HORIZONTAL)
        hbox.Add(self.processDisplay, flag=flagsR, border=2)
        hbox.AddSpacer(10)
        self.fetchBt = wx.Button(
            self, label='Processing', style=wx.BU_LEFT, size=(100, 23))
        self.fetchBt.Bind(wx.EVT_BUTTON, self.onStartExp)
        hbox.Add(self.fetchBt, flag=flagsR, border=2)
        self.fetchBt.Enable(False)
        sizer.Add(hbox, flag=flagsR, border=2)
        return sizer

#--PanelSetting----------------------------------------------------------------
    def onStartExp(self, event):
        """ Start the experiment."""
        csvFtag = 'M'if self.mode == 0 else 'D'
        gv.iDataMgr.setPanelData(csvFtag)
        # Force update the display panel.
        if self.mode == 0 and gv.iChartPanel0:
            pass
            #gv.iChartPanel0.updateDisplay()
        elif gv.iChartPanel1:
            gv.iChartPanel1.updateDisplay()
        gv.iMainFame.infoWinClose(None)

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
        # Show the process bar increase. 
        waitT = 0.2 if self.mode == 0 else 0.1
        for i in range(1,11):
            self.processDisplay.SetValue(i)
            time.sleep(waitT)
        # Load CSV tag
        csvFtag = 'M'if self.mode == 0 else 'D'
        gv.iDataMgr.loadCSVData(csvFtag)
        self.fetchBt.SetLabel("Finished")    
        self.fetchBt.Enable(True)

#--PanelSetting----------------------------------------------------------------
    def setCellVals(self):
        """ Load the default value to the cells. """
        dataList = gv.EXP_CONFIG[:3] if self.mode == 0 else [gv.EXP_CONFIG[-1]]
        for rIdx, item in enumerate(dataList):
            for cIdx, data in enumerate(item):
                self.grid.SetCellValue(rIdx, cIdx, data)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelCPResult(wx.Panel):
    """ Panel to show the experiment ROC compare result."""
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(620, 420))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.sampleNum = 420
        self.SetSizer(self._buidUISizer())
        self.Layout()

#--PanelCPResult---------------------------------------------------------------
    def _buidUISizer(self):
        """ Build the Panel UI"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        flagsR = wx.RIGHT  # wx.ALIGN_CENTER_VERTICAL
        sizer.Add(wx.StaticText(
            self, label=" Data Comparision Control"), flag=flagsR, border=2)
        sizer.AddSpacer(10)
        self.cpModeCH0 = wx.ComboBox(
            self, -1, choices=['Compare Method: ROC'], style=wx.CB_READONLY)
        self.cpModeCH0.SetSelection(0)
        sizer.Add(self.cpModeCH0, flag=flagsR, border=2)
        sizer.AddSpacer(10)
        self.cpBaseCH = wx.ComboBox(
            self, -1, choices=['Compare Base: None', 'Compare Base: exp-data.csv'], style=wx.CB_READONLY)
        self.cpBaseCH.SetSelection(0)
        sizer.Add(self.cpBaseCH, flag=flagsR, border=2)
        sizer.AddSpacer(10)
        self.dataTLb = wx.StaticText(
            self, label=" Data Type: Type 5: Input/Output Delay (Type 2 + Type 3)")
        sizer.Add(self.dataTLb, flag=flagsR, border=2)
        sizer.AddSpacer(10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.startBt = wx.Button(
            self, label='Start to match data.', style=wx.BU_LEFT, size=(180, 23))
        self.startBt.Bind(wx.EVT_BUTTON, self.startMatch)
        hbox.Add(self.startBt, flag=flagsR, border=2)
        self.processDisplay = wx.Gauge(
            self, range=4, size=(415, 22), style=wx.GA_HORIZONTAL)
        hbox.Add(self.processDisplay, flag=flagsR, border=2)
        sizer.Add(hbox, flag=flagsR, border=2)
        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(8, 3)
        self.grid.SetRowLabelSize(180)
        # Set the column labels
        self.grid.SetColSize(0, 140)
        self.grid.SetColSize(1, 140)
        self.grid.SetColSize(2, 140)
        self.grid.SetColLabelValue(0, 'exp-localHost')
        self.grid.SetColLabelValue(1, 'exp-netStorage')
        self.grid.SetColLabelValue(2, 'exp-remHost')
        # Set the row labels.
        self.grid.SetRowLabelValue(0, 'Minimum Threshold')
        self.grid.SetRowLabelValue(1, 'Maximum Threshold')
        self.grid.SetRowLabelValue(2, 'True Positive')
        self.grid.SetRowLabelValue(3, 'True Negative')
        self.grid.SetRowLabelValue(4, 'False Positive')
        self.grid.SetRowLabelValue(5, 'False Negative')
        self.grid.SetRowLabelValue(6, 'Sensitivity: tp/(tp+fn) ')
        self.grid.SetRowLabelValue(7, 'Specifity: tn/(tn+fp)')
        sizer.Add(self.grid, flag=flagsR, border=2)
        sizer.AddSpacer(10)
        self.bestFTLb = wx.StaticText(self, label="Best Fit Data Set: None")
        sizer.Add(self.bestFTLb, flag=flagsR, border=2)
        sizer.AddSpacer(10)
        self.restBt = wx.Button(
            self, label='Reset all to defualt', style=wx.BU_LEFT, size=(180, 23))
        self.restBt.Bind(wx.EVT_BUTTON, self.clearAll)
        sizer.Add(self.restBt, flag=flagsR, border=2)
        sizer.AddSpacer(10)
        self.loadtoPanelBt = wx.Button(
            self, label='Load to compare panel', style=wx.BU_LEFT, size=(180, 23))
        self.loadtoPanelBt.Bind(wx.EVT_BUTTON, self.loadtoPanel)
        sizer.Add(self.loadtoPanelBt, flag=flagsR, border=2)
        return sizer

#--PanelCPResult---------------------------------------------------------------
    def clearAll(self):
        """ Clear all the data in the grid. """
        for cIdx in range(3):
            for rIdx in range(8):
                self.grid.SetCellValue(rIdx, cIdx, '')

#--PanelCPResult---------------------------------------------------------------
    def loadtoPanel(self, event):
        """ Load the compare data to the control panel."""
        idxF = 0
        for idx, val in enumerate(gv.iChartPanel1.dataD[0]):
            if val > 3:
                idxF = idx
                break
        # only copy 420 sample to compare panel.
        if len(gv.iChartPanel1.dataD[0]) - idxF < self.sampleNum:
            idxF = len(gv.iChartPanel1.dataD[0]) - self.sampleNum
        gv.iChartPanel3.compareOverlay = True
        gv.iChartPanel3.shiftOffset = idxF//10
        gv.iChartPanel3.dataD[2] = gv.iChartPanel0.dataD[2][idxF:idxF+self.sampleNum]
        gv.iChartPanel3.dataD[-1] = gv.iChartPanel1.dataD[0][idxF:idxF+self.sampleNum]
        # make the end value to be 0
        gv.iChartPanel3.dataD[2][0] = 0
        gv.iChartPanel3.dataD[-1][0] = 0
        gv.iChartPanel3.dataD[2][-1] = 0
        gv.iChartPanel3.dataD[-1][-1] = 0
        gv.iChartPanel3.updateDisplay()

#--PanelCPResult---------------------------------------------------------------
    def fillInData(self, cIdx, dataSet):
        """ Fill the matching result in the data. """
        if len(dataSet) != 8:
            print("The data set is invalid: %s" % str(dataSet))
        for rIdx in range(8):
            self.grid.SetCellValue(rIdx, cIdx, str(dataSet[rIdx]))
        # temporary add this for the demo.
        if cIdx == 2:
             self.bestFTLb.SetLabel("Best Fit Data Set: exp-remHost")

#--PanelCPResult---------------------------------------------------------------
    def startMatch(self, event):
        """ Set the data match flag. """
        gv.iDataMgr.matchFlag = 0
        self.processDisplay.SetValue(gv.iDataMgr.matchFlag+1)
