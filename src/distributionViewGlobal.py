#-----------------------------------------------------------------------------
# Name:        distributionViewGlobal.py
#
# Purpose:     This module is used set the Local config file as global value 
#              which will be used in the other modules.
# Author:      Yuancheng Liu
#
# Created:     2019/08/01
# Copyright:   NUS-Singtel Cyber Security Research & Development Laboratory
# License:     YC @ NUS
#-----------------------------------------------------------------------------
import os, sys

dirpath = os.getcwd()
print("distributionViewGlobal: Current working directory is : %s" %dirpath)

WINP = sys.platform.startswith('win')

# Application name and version. setting
APP_NAME = 'NetFetcher Distribution Data Viewer'
# program title icon
ICON_PATH = "".join([dirpath, "\\img\\title.png"]) if WINP else "".join([dirpath, "/img/title.png"])
# module folder:
MODE_F_PATH = "".join([dirpath, "\\model\\*.csv"]) if WINP else "".join([dirpath, "/model/*.csv"])
# Data folder:
DATA_F_PATH = "".join([dirpath, "\\data\\*.csv"]) if WINP else "".join([dirpath, "/data/*.csv"])
# The config file for the netfetcher program.
CONFIG_FILE = ("model_scripted_exp.bat", "check_scripted_exp.bat")

iMainFame = None    # mail frame
iDataMgr = None     # data manager.
iChartPanel0 = None # History chart panel for module
iChartPanel1 = None # History chart panel
iSetupPanel = None
iCPMode = True
iModelType = 5      # Model Type currently displayed
iDataType = 5       # Data Type currently displayed
iUpdateRate = 2     # Time period to update the 
iLineStyle = 1

