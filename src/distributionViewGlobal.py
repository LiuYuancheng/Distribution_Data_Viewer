#-----------------------------------------------------------------------------
# Name:        XAKAsensorGlobal.py
#
# Purpose:     This module is used set the Local config file as global value 
#              which will be used in the other modules.
# Author:      Yuancheng Liu
#
# Created:     2019/07/05
# Copyright:   NUS – Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import os

dirpath = os.getcwd()
print("XAKAsensorGlobal: Current working directory is : %s" %dirpath)

# Application name and version. setting
APP_NAME = 'NetFetcher Distribution Data Viewer'

iChartPanel0 = None      # History chart panel
iChartPanel1 = None      # History chart panel