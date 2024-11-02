# Data Transmission Latency SIEM Log Analysis Dashboard

**Program Design Purpose**: The Data Transmission Latency SIEM Log Analysis Dashboard is designed to provide comprehensive visualization and analysis of data transmission latencies within a company’s network, focusing on the latency between cloud, server, and individual nodes. This dashboard aggregates delay data collected from omnibus netFetcher peer-to-peer node latency measurements. By displaying and comparing predicted latency models with real-time data, the dashboard allows for in-depth analysis using Receiver Operating Characteristic (ROC) curve comparisons. This enables the identification of deviations in transmission latency that may signal potential network security threats, such as traffic mirroring, ARP spoofing, and Man-in-the-Middle (MITM) attacks. Through these features, the dashboard enhances situational awareness and supports proactive threat detection and mitigation in networked environments.

```python
# Version:     v0.1.2
# Created:     2024/11/01
# Copyright:   Copyright (c) 2024 LiuYuancheng
# License:     MIT License 
```

**Table of Contents**

[TOC]

------

### Introduction 

The **Data Transmission Latency Log Distribution Data Viewer** project aims to create a specialized tool for visualizing and analyzing experimental network latency data captured by the netFetcher module. This module is used to record various delay metrics across different file types—ranging from small files (such as an images file) to large files (such as Ubuntu ISO file), while downloading from multiple servers. By visualizing this data, the Distribution Data Viewer will provide insights into the latency behaviors associated with different file sizes and transfer conditions.

The tool supports comprehensive visualization features, allowing users to load and plot experimental data from multiple CSV files. Using this data, the Viewer generates distribution curves and includes a comparison functionality to help users find the best-matching data set. This comparison employs a Receiver Operating Characteristic (ROC) curve algorithm, enabling effective performance assessment of latency predictions against actual measurements. The key feature includes:

- **Latency Visualization**: To display the captured network latency data across various network segments, including cloud-to-router, router-to-switch, and switch-to-peer transfers. This data is sourced from Fortinet Firewire, internal network switches, and the Omnibus netFetcher module.
- **Model vs. Real Data Comparison**: To implement a Receiver Operating Characteristic (ROC) comparison algorithm that contrasts actual latency data with predictive model outputs. This helps in identifying abnormal data transmission patterns.
- **Anomaly Detection for Security**: By benchmarking current latency against normal patterns, the system aims to detect and alert for potential security threats such as traffic mirroring, ARP spoofing, and Man-in-the-Middle (MITM) attacks.



#### Distribution Data Viewer Main UI

The main UI of the Distribution Data Viewer provides two primary display modes, controlled by the `iCPMod` flag in the global configuration file `distributionViewGlobal.py`:

**Normal Parallel Display Mode**: This mode presents measured latency data at the top of the screen, with calculated values displayed at the bottom for straightforward comparison. The screen shot is shown below:

![](doc/distrubution_UI.gif)



**Compare Overlay Mode**: This mode overlays both the measured and calculated data on a single graph, allowing for direct visual comparison of the distribution patterns. The screen shot is shown below:

![](doc/normal_dis_mode.png)



------

### Data Sources Detail

The data for this project is collected from three critical network components: the firewall router, internal network switch, and download client node. Six types of latency metrics are gathered, each offering insights into potential network issues or security threats:

##### Type 0: Timestamping Difference

- Measures clock discrepancies across the firewall, internal switch, and download computer to ensure that all logs are synchronized to a unified time standard. This alignment is essential for accurate latency comparisons.

##### Type 1: Server Request Preprocessing Delay

- To measure server response time, we first ping the server to record an initial response time `t0`. Then, the interval `t1 − t0` is calculated by measuring the time `t1`, from sending the download request to receiving the response, yielding the server’s processing delay.
- The measurement procedure detail diagram is shown below:

![](doc/img/rm_05.png)

##### Type 2: Firewall Transmission Latency

- This captures the time taken by the firewall to process outgoing download requests and receive responses from the external server. The latency is defined as the interval `t1−t0`, where `t0` is the send time and `t1` is the receive time. A significant deviation between model predictions (normal situation) and logged values may indicate a potential MITM or traffic mirroring attack occurred between the firewall and the download server.
- The measurement procedure detail diagram is shown below:

![](doc/img/rm_06.png)

##### Type 3: Internal Switch Transmission Latency

- Measures the time taken for the internal switch to relay download requests to the firewall and receive responses back. This interval is represented as `t3−t2`. If the firewall latency (Type 2) appears normal but this metric shows anomalies, it may suggest a MITM or traffic mirroring attack between the firewall and the switch.
- The measurement procedure detail diagram is shown below:

![](doc/img/rm_07.png)

##### Type 4: Download Client Observed Delay

- The time interval between the client sending a request to the internal switch and receiving the response. Calculated as `t5−t4`, this metric provides insights into end-to-end delay observed at the download client. If other latencies appear stable but this metric diverges, it may indicate a MITM or traffic mirroring attack between the switch and the download node.
- The measurement procedure detail diagram is shown below:

![](doc/img/rm_08.png)



##### Type 5: I/O and Transfer Delay

- This is the cumulative delay from Types 2 and 3, including additional network transfer times, providing an overall view of data transfer latency.

This revised description emphasizes the purpose and implications of each data type, offering a clearer view of how each metric contributes to understanding network health and security.



------

### System Design 

The Data Transmission Latency SIEM Log Analysis Dashboard is designed to visualize and analyze data transmission delays to detect potential network security issues, such as Man-in-the-Middle (MitM) attacks or traffic mirroring. By comparing observed latency data with expected "normal" latency distributions, the system can highlight significant deviations that indicate abnormal network behavior, as shown in the diagram below: 

 ![](doc/img/rm_09.png)

When an attack like MitM occurs, the network traffic is rerouted through an attacker’s node before reaching the user’s device, introducing a noticeable increase in transmission latency. This system aims to capture and visualize such delays to support timely detection and response. The system workflow diagram is shown below:

![](doc/img/rm_10.png)

**Attack Scenarios and Latency Indicators:**

1. **Firewall Transmission Latency:** A significant discrepancy between the measured and expected firewall transmission latency could indicate a MitM or traffic mirroring attack between the firewall and the download server.
2. **Internal Switch Transmission Latency:** If the firewall latency distribution appears normal, but the internal switch latency shows abnormal discrepancies, this may point to a potential attack between the firewall and the switch.
3. **Download Client Observed Delay:** If both firewall and switch latencies are within normal ranges, but the client-observed latency is abnormal, this could indicate an attack between the switch and the download computer.

#### Program Main Function Design

The main functions of the Viewer are outlined as follows:

**Dynamic Data Visualization:** The viewer dynamically updates the data view, including line styles, percentile display, and font formatting, to ensure clear presentation of latency distribution data.

**ROC-Based Data Comparison:** Using Receiver Operating Characteristic (ROC) curve analysis, the viewer calculates and compares the current sample set’s performance metrics with the model data to determine the likelihood of attacks. This includes calculating values such as:

- **Minimum and Maximum Difference Thresholds**
- **True Positive and True Negative Rates**
- **False Positive and False Negative Rates**
- **Sensitivity**: Sensitivity = `True Positive / (True Positive+False Negative)`
- **Specificity**: Specificity = `True Negative/ (True Negative+False Positive)` 

**Overlay Graph Comparison Results:** The viewer overlays graphs of normal and current latency distributions, providing a visual representation of discrepancies. This is essential for highlighting potential anomalies caused by network attacks.



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

