# Data Transmission Latency SIEM Log Analysis Dashboard

**Program Design Purpose**: The Data Transmission Latency SIEM Log Analysis Dashboard is designed to provide comprehensive visualization and analysis of data transmission latencies within a company’s network, focusing on the latency between cloud, server, and individual nodes. This dashboard aggregates delay data collected from omnibus netFetcher peer-to-peer node latency measurements. By displaying and comparing predicted latency models with real-time data, the dashboard allows for in-depth analysis using Receiver Operating Characteristic (ROC) curve comparisons. This enables the identification of deviations in transmission latency that may signal potential network security threats, such as traffic mirroring, ARP spoofing, and Man-in-the-Middle (MITM) attacks. Through these features, the dashboard enhances situational awareness and supports proactive threat detection and mitigation in networked environments.

**Table of Contents**

[TOC]

------

### Introduction 

The **Data Transmission Latency Log Distribution Data Viewer** project aims to create a specialized tool for visualizing and analyzing experimental network latency data captured by the netFetcher module. This module is used to record various delay metrics across different file types—ranging from small files (such as an images file) to large files (such as Ubuntu ISO file), while downloading from multiple servers. By visualizing this data, the Distribution Data Viewer will provide insights into the latency behaviors associated with different file sizes and transfer conditions.

The tool supports comprehensive visualization features, allowing users to load and plot experimental data from multiple CSV files. Using this data, the Viewer generates distribution curves and includes a comparison functionality to help users find the best-matching data set. This comparison employs a Receiver Operating Characteristic (ROC) curve algorithm, enabling effective performance assessment of latency predictions against actual measurements. The key feature includes:

- **Latency Visualization**: To display the captured network latency data across various network segments, including cloud-to-router, router-to-switch, and switch-to-peer transfers. This data is sourced from Fortinet Firewire, internal network switches, and the Omnibus netFetcher module.
- **Model vs. Real Data Comparison**: To implement a Receiver Operating Characteristic (ROC) comparison algorithm that contrasts actual latency data with predictive model outputs. This helps in identifying abnormal data transmission patterns.
- **Anomaly Detection for Security**: By benchmarking current latency against normal patterns, the system aims to detect and alert for potential security threats such as traffic mirroring, ARP spoofing, and Man-in-the-Middle (MITM) attacks.



#### **Distribution Data Viewer Main UI**

The main UI of the Distribution Data Viewer provides two primary display modes, controlled by the `iCPMod` flag in the global configuration file `distributionViewGlobal.py`:

**Normal Parallel Display Mode**: This mode presents measured latency data at the top of the screen, with calculated values displayed at the bottom for straightforward comparison. The screen shot is shown below:

![](doc/distrubution_UI.gif)



**Compare Overlay Mode**: This mode overlays both the measured and calculated data on a single graph, allowing for direct visual comparison of the distribution patterns. The screen shot is shown below:

![](doc/normal_dis_mode.png)



------

### Data Sources Detail

The data is collected from firewall router, internal switch and the download node, there are 6 types of data to be collected: 

**Type 0: Timestamping difference** 

Clock difference between firewall device, internal switch and the download computer to make sure all the logs data a use the same time standard. 

**Type 1: Server Request Preprocessing Delay** 

We use ping to get the server response time t0, then record the time value t1 between we send the download request get the download response, then user t1 - t0 to get the time of server processing the download request. 

![](doc/img/rm_05.png)



**Type 2: Firewall transmission latency**

The time interval between firewall send the download to outside to the firewall accept the download response from the file server.  If this data get big difference between module and log, which means there may be MiTM, or traffic mirroring attack between the firewall and the download server. 

**Type 3: Internal switch transmission latency**

The time interval between the switch send the download to firewall to the switch accept the download response from the firewall.   If the type 2 distribution is normal and this data get big difference between module and log, which means there may be MiTM, or traffic mirroring attack between the firewall and the switch. 

**Type 4: Download Client Observed Delay** 

The time interval between the download client send to the internal switch to the download client get the download response from the internal switch. If the type 3 distribution is normal and this data get big difference between module and log, which means there may be MiTM, or traffic mirroring attack between the switch and the download node. 

**Type 5: I/O and Transfer Delay** 

Sum of Types 2 and 3, including network delay 



------





#### Program Main Function

The main function of the Viewer 

1. Visualize different kinds of delay data with different data sampling rate. 

   | The data viewer will show 6 types of file transfer delay data which collected by the netFetcher program: |
   | ------------------------------------------------------------ |
   | Type 0: Timestamping Delay [Time clock delay/difference between server and client.] |
   | Type 1: Download Server Request Preprocessing Delay          |
   | Type 2: Download Server Disk Seek Delay                      |
   | Type 3: Download Server Disk Read Delay                      |
   | Type 4: Client Observed Delay (Time[get the download package] - Time[send the download request] ) |
   | Type 5:I/O+transfer Delay (Type 2 + Type 3 + Network delay)  |

2. Dynamically update the data view, line style, percentile of data, font format. 
3. Calculate the current model and measured data sample set's ROC comparison value for different three kinds of data set : `data minimum diference threshold` ,  `data maximum difference threshold` , `model match to measurement true positive rate` , `model match to measurement true negative rate` , `model match to measurement false positive rate`, `model match to measurement false negative rate`, `sensitivity [true positive/(true positive+false negative)]` , `specifity [true negative/(true negative + false positive)]`

4. Show the overly graph comparison result. 
5. --



------

### Program Setup

###### Development Environment : python 3.7.10

###### Additional Lib/Software Need

1. **Wxpython 4.0x**  https://wxpython.org/pages/downloads/index.html

   ```
   Installation cmd: pip install -U wxPython
   ```

2. **Numpy**  https://pypi.org/project/numpy/

   ```
   Installation cmd: pip install numpy
   ```

3. -- 

###### Hardware Needed : None

###### Program Files List 

version: V_0.2

| Program File                  | Execution Env | Description                                 |
| ----------------------------- | ------------- | ------------------------------------------- |
| src/distributionViewer.py     | python 3      | Program UI main frame and data manager API. |
| src/distributionViewGlobal.py | python 3      | Function panel module.                      |
| src/distributionViewGlobal.py | python 3      | Global parameter file.                      |
| src/ run.bat                  |               | Windows auto run file.                      |
| src/check_sripted_exp.bat     | netfetcher    | netfetcher check config file.               |
| src/model_scripted_exp.bat    | netfetcher    | netfetcher model calculation config file.   |
| src/img                       |               | Program needed image file folder.           |
| src/data                      |               | Measurement data csv file storage folder.   |
| src/model                     |               | Modeling data csv file storage folder.      |



------

### Program Usage

###### Program Execution 

To run the program, go/cd to the src folder and run the "distributionViewer.py" program by:

```
python distributionViewer.py
```

The tested data CSV files are in the '`data`' and '`model`' folder, the folder structure should be:

![](doc/folderStructure.png)

###### Program Data Display Selection

We use the compare mode as an example to show how to use the program: 

1. Click `setup` button to select data source from the title bar: 

   ![](doc/dataSelection.png)

   Select the data set you want to display in the data set selection popup window: 

   ![](doc/dataSet.png)

   Fill in the data and click the "`Calibration`" button, then the related netFetcher execution configuration *.bat file will be created, then press the "BatchRun" button the netFetcher program will be executed and the related data will be put in "Model" and "data" folder. When the data calibration finished the `processing` button will change to `finish`, then press the `finish` button. 

2. Select the date type you want to display in the drop down menu as shown in the video: 

   https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/Video_2019-08-22_104710.wmv
   
   https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/Video_2019-08-22_105055.wmv
   
3. Select display different type of data and the Y-Axis scale format with the drop down menu in the title bar. Currently we provide 3 kinds of Y-Axis scale: 

   | Y-Axis scale type       | Scale range               | Data covered               |
   | ----------------------- | ------------------------- | -------------------------- |
   | Logarithmic scale: 10^n | [1, 10, 100, 1000, 10000] | All data                   |
   | Linear scale: Dynamic   | [1/10*max] *range(1, 11 ) | All data                   |
   | Linear scale: Fixed     | 20*range(1,11)            | occurrences  less than 200 |

   The fixed Y-Axis mode is shown below:

   ![](doc/fixedView.png)



3. Click the "compare mode" check box, both the [Model] and [data] data will be drawn overlay on the model display panel: 

   ![](doc/compare_dis_mode.png)

4. -- 



###### Program Display Config Selection 

- The user can change the display setting in the button display setting bar: ![](doc/displayConfig.png)

- The mode data display rate can be change in 2sec ~ 5 sec. The program will sample count and data percentile can also be changed from the drop down menu. 

- Press the "`Font Selection`" button the font change window will pop-up: 

  <img src="doc/fontChange.png" style="zoom: 80%;" />

- Check the "Synchronized Adjust" check box the [model] and [data] display will show the same change when user change one of the data display selection setting. 




###### Use Program to Find The Best Match Data

This is the receiver operating characteristic curve compare algorithm control panel used to find the best match data: 

![](doc/readMe2.png)

**Step 1**: In the data comparison control panel, select the compare method: (Currently only have one compare method which compare 2 curve's ROC )

ROC compare doc link: https://ncss-wpengine.netdna-ssl.com/wp-content/themes/ncss/pdf/Procedures/NCSS/Comparing_Two_ROC_Curves-Paired_Design.pdf

**Step 2**: Select the compare base data from the drop down menu.

**Step 3**: Click the "Start to match data" button, the program will start to calculate the data's ROC and find the best sensitivity data. The orignal data will be shown in the table. 

```
Minimum Threshold: 19631.183700649814
Maximum Threshold: 19631.183700649814
True Positive: 28803
True Negative: 16668
False Positive: 11575
False Negative: 1055
Sensitivity: tp/(tp+fn) = 0.9646660861410677
Specifity: tn/(tn+fp) = 0.5901639344262295
Minimum Threshold: 209266.451635113
Maximum Threshold: 209279.2085214074        
True Positive: 14964
True Negative: 15120
False Positive: 14878
False Negative: 15030
Sensitivity: tp/(tp+fn) = 0.4988997799559912
Specifity: tn/(tn+fp) = 0.5040336022401494  
```

**Step 4**: Click the "Load to compare panel"  button, the best match data and the compare base data will be plot overlay with each other on the compare panel as shown below: 

<img src="doc/readMe3.png" style="zoom:80%;" />

**Step 5:**  -- 



------

### Problem and Solution

###### Problem: 

**OS Platform** : 

**Error Message**: 

**Type**: 

**Solution**:

**Related Reference**:  



------

### Reference Links

- https://ncss-wpengine.netdna-ssl.com/wp-content/themes/ncss/pdf/Procedures/NCSS/Comparing_Two_ROC_Curves-Paired_Design.pdf
- https://github.com/chef/omnibus/blob/main/lib/omnibus/fetchers/net_fetcher.rb
- 

------

> Last edit by LiuYuancheng(liu_yuan_cheng@hotmail.com) at 05/12/2021

