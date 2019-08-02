#-----------------------------------------------------------------------------
# Name:        XAKAsensorGlobal.py
#
# Purpose:     This module is used set the Local config file as global value 
#              which will be used in the other modules.
# Author:      Yuancheng Liu
#
# Created:     2019/08/01
# Copyright:   NUS – Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------

import os

dirpath = os.getcwd()
print("XAKAsensorGlobal: Current working directory is : %s" %dirpath)

# Application name and version. setting
APP_NAME = 'NetFetcher Distribution Data Viewer'


MODE_F_PATH = "".join([dirpath, "\\module\\short_rc_exp10.csv"])
DATA_F_PATH = "".join([dirpath, "\\data\\short_sc_exp10.csv"])

iDataMgr = None
iChartPanel0 = None      # History chart panel
iChartPanel1 = None      # History chart panel