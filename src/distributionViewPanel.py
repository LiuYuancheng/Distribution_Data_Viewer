
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
import wx.grid

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelChart(wx.Panel):
    """ This function is used to provide lineChart wxPanel to show the all the 
        data as a distribution line.
    """
    def __init__(self, parent, dataSetNum, appSize=(1600, 290), recNum=750):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(appSize[0], 290))
        self.SetBackgroundColour(wx.Colour(200, 210, 200))
        self.recNum = recNum    # hole many revode we are going to show.
        self.appSize = appSize
        self.updateFlag = True  # flag whether we update the diaplay area
        self.colorIdx = 0       # color index.
        self.dataSetNum = dataSetNum
        self.dataD =[[0]*recNum for _ in range(dataSetNum)]
        self.times = [n for n in range(self.recNum//10)] # X-Axis.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.maxCount = 0 
    def clearData(self):
        self.dataD =[[0]*self.recNum for _ in range(self.dataSetNum)]

#--PanelChart--------------------------------------------------------------------
    def appendData(self, numsList):
        """ Append the data into the data hist list.
            numsList Fmt: [(current num, average num, final num)]
        """
        self.data.append([min(n, 20)for n in numsList])
        self.data.pop(0) # remove the first oldest recode in the list.
    
#--PanelChart--------------------------------------------------------------------
    def drawBG(self, dc):
        """ Draw the line chart background."""
        dc.SetPen(wx.Pen('WHITE'))
        dc.DrawRectangle(1, 1, self.appSize[0], 205)
        # DrawTitle:
        font = dc.GetFont()
        font.SetPointSize(8)
        dc.SetFont(font)
        dc.DrawText('NetFetcher Data Distribution', 2, 245)
        dc.DrawText('occurences[x10]', -35, 225)
        dc.DrawText('Delay[x1000 ns]', 700, -25)

        # Draw Axis and Grids:(Y-people count X-time)
        dc.SetPen(wx.Pen('#D5D5D5')) #dc.SetPen(wx.Pen('#0AB1FF'))
        w, _ = self.appSize 
        dc.DrawLine(1, 1, w, 1)
        dc.DrawLine(1, 1, 1, w)

        self.maxCount= max([max(i) for i in self.dataD])


        for i in range(2, 22, 2):
            dc.DrawLine(2, i*10, w, i*10) # Y-Grid
            dc.DrawLine(2, i*10, -5, i*10)  # Y-Axis
            dc.DrawText(str(self.maxCount//20*i), -25, i*10+5)  # format to ## int, such as 02



        for i in range(len(self.times)): 
            dc.DrawLine(i*20, 2, i*20, 200) # X-Grid
            dc.DrawLine(i*20, 2, i*20, -5)  # X-Axis
            dc.DrawText(str(self.times[i]).zfill(2), i*20-5, -5)
        
#--PanelChart--------------------------------------------------------------------
    def drawFG(self, dc):
        """ Draw the front ground data chart line."""
        # draw item (Label, color)
        #item = (('Data1', '#0AB1FF'), ('Data2', '#CE8349'), ('Data3', '#A5CDAA'))
        item = (('Data1', 'RED'), ('Data2', '#A5CDAA'), ('Data3', 'BLUE'))

        for idx in range(len(self.dataD)):
            (label, color) = item[idx]
            # Draw the line sample.
            dc.SetPen(wx.Pen(color, width=1, style=wx.PENSTYLE_SOLID))
            dc.DrawText(label, idx*200+150, 220)
            dc.DrawLine(100+idx*60, 212, 100+idx*60+8, 212)
            
            dc.DrawSpline([(int(i*2+idx*2), int(self.dataD[idx][i])*200//self.maxCount) for i in range(self.recNum)])


#--PanelChart--------------------------------------------------------------------
    def updateDisplay(self, updateFlag=None):
        """ Set/Update the display: if called as updateDisplay() the function will 
            update the panel, if called as updateDisplay(updateFlag=?) the function 
            will set the self update flag.
        """
        if updateFlag is None and self.updateFlag: 
            self.Refresh(True)
            self.Update()
        else:
            self.updateFlag = updateFlag

#--PanelChart--------------------------------------------------------------------
    def OnPaint(self, event):
        """ Main panel drawing function."""
        dc = wx.PaintDC(self)
        # set the axis orientation area and fmt to up + right direction.
        dc.SetDeviceOrigin(40, 250)
        dc.SetAxisOrientation(True, True)
        self.drawBG(dc)
        self.drawFG(dc)

    def periodic(self, event):
        """ Call back every periodic time."""
        # Set the title of the frame.
        self.SetTitle( ' '.join((gv.APP_NAME, datetime.now().strftime("[ %m/%d/%Y, %H:%M:%S ]"))))
        if gv.iEmgStop: return
        timeStr = time.time()
        self.mapPanel.periodic(timeStr)




#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class PanelSetting(wx.Panel):
    """  Setting panel used to show the 
    """
    def __init__(self, parent):
        """ Init the panel."""
        wx.Panel.__init__(self, parent, size=(620, 250))
        self.SetBackgroundColour(wx.Colour(200, 200, 210))
        self.SetSizer(self.buidUISizer())

#--PanelMultInfo---------------------------------------------------------------
    def buidUISizer(self):
        """ Build the UI with 2 columns.left: Map, right: sensor data Grid."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        flagsT, flagsR = wx.RIGHT, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticText(self, label="Fill The Information In The Grid: "), flag=flagsR, border=2)
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(640, -1), style=wx.LI_HORIZONTAL), flag=flagsR, border=2)
        sizer.AddSpacer(5)

        sizer.AddSpacer(5)
        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(5, 6)
        # Set the Grid size.
        self.grid.SetRowLabelSize(40)
        self.grid.SetColSize(0, 80)
        self.grid.SetColSize(1, 80)
        self.grid.SetColSize(2, 80)
        self.grid.SetColSize(3, 80)
        self.grid.SetColSize(4, 80)
        self.grid.SetColSize(5, 150)
        # Set the Grid's labels.
        self.grid.SetColLabelValue(0, 'IP address')
        self.grid.SetColLabelValue(1, 'Port NUm ')
        self.grid.SetColLabelValue(2, 'File ID ')
        self.grid.SetColLabelValue(3, 'Block Num')
        self.grid.SetColLabelValue(4, 'Iterations ')
        self.grid.SetColLabelValue(5, 'Output file')
        #self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.highLightMap)
        sizer.Add(self.grid, flag=flagsR, border=2)
        sizer.AddSpacer(5)
        self.pauseBt = wx.Button(self, label='Construct Model', style=wx.BU_LEFT, size=(100, 23))
        sizer.Add(self.pauseBt, flag=wx.ALIGN_CENTER_HORIZONTAL, border=2)
        return sizer

#--PanelMultInfo---------------------------------------------------------------
    def updateSensorIndicator(self, idx, state):
        """ Update the sensor indictor's status Green:online, Gray:Offline."""
        color = wx.Colour("GREEN") if state else wx.Colour(120, 120, 120)
        self.senIndList[idx].SetBackgroundColour(color)

#--PanelMultInfo---------------------------------------------------------------
    def updateSensorGrid(self, idx, dataList):
        """ Update the sensor Grid's display based on the sensor index. """
        if len(dataList) != 3:
            print("PanelMultInfo: Sensor Grid fill in data element missing.")
            return
        # Udpate the grid cells' data.
        totPllNum = totPllAvg = 0
        for i, item in enumerate(dataList):
            dataStr = "{0:.4f}".format(item) if isinstance(
                item, float) else str(item)
            self.grid.SetCellValue(idx, i, dataStr)
            if i == 1: totPllNum += item
            if i == 2: totPllAvg += item
        # update the total numbers. 
        self.grid.SetCellValue(4, 0, str(self.sensorCount))
        self.grid.SetCellValue(4, 1, "{0:.4f}".format(totPllNum))
        self.grid.SetCellValue(4, 2, "{0:.4f}".format(totPllAvg))
        self.grid.ForceRefresh()  # refresh all the grid's cell at one time ?
        
#--PanelMultInfo---------------------------------------------------------------
    def markSensorRow(self, idx):
        """ Mark(highlight)the selected row."""
        self.grid.SelectRow(idx)

#--PanelMultInfo---------------------------------------------------------------
    def highLightMap(self, event):
        """ High light the sensor covered area on the topview map."""
        row_index = event.GetRow()
        self.grid.SelectRow(row_index)
        # covert 0->(0, 0) 1->(1, 0), 2->(0, 1), 3->(1, 1)
        self.mapPanel.highLightPos = (row_index % 2, row_index//2) 
