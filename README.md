# Distribution_Data_Viewer

##### This project will create a distribution data viewer to show the experiment result of the netFetcher.(Load all the experiment CSV file and create the distribution curve.)

 

| The data viewer will show 6types of file transfer delay data which collected by the netFetcher program: |
| ------------------------------------------------------------ |
| Type 0: Timestamping Delay                                   |
| Type 1: Preprocessing Delay                                  |
| Type 2: Disk Seek Delay                                      |
| Type 3: Disk Read Delay                                      |
| Type 4: Client Observed Delay                                |
| Type 5: Input+Output Delay (Type 2 + Type 3)                 |

---
###### User Interface and Display Mode: 

The distribution data viewer has 2 display mode: **Parallel display mode** and  **Compare display mode**

Parallel display mode:

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_102527.png)

Compare display mode:

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_102419.png)

This is the cmd to install 

[wxPython]: https://wxpython.org/pages/downloads/index.html:	"wxPython"

```
pip install -U wxPython
```

This is the cmd to install 

[numpy]: https://pypi.org/project/numpy/:	"numpy"

```
pip install numpy
```

(The numpy should be auto-installed when you installed the wxpython)

To run the program, go/cd to the src folder and run the "distributionViewer.py" program by:

```
python distributionViewer.py
```

The tested data CSV files are in the 'data' and 'model' folder, the folder structure should be:

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/folderStructure.png)

------

###### Program Data Display Selection : 

We use the compare mode to show how to use the program: 

Data source title bar: 

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_104832.png)

=> User can select to display different type of data and the Y-Axis scale format. Currently we provide 3 kinds of Y-Axis scale: 

| Y-Axis scale type       | Scale range               | Data covered               |
| ----------------------- | ------------------------- | -------------------------- |
| Logarithmic scale: 10^n | [1, 10, 100, 1000, 10000] | All data                   |
| Linear scale: Dynamic   | [1/10*max] *range(1, 11 ) | All data                   |
| Linear scale: Fixed     | 20*range(1,11)            | occurrences  less than 200 |

Fixed Y-Axis mode:

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/fixedView.png)

Press the "Setup" button the setup window will pop up: 

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/setup.png)

=> Fill in the data and click the "Calibration" button then the related netFetcher execution configuration *.bat file will be created, then press the "BatchRun" button the netFetcher program will be executed and the related data will be put in "Model" and "data" folder.

Click the "compare mode" check box, both the [Model] and [data] data will be drawn on the Model display panel: 

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_104846.png)

------

###### Program Display Setting: 

The display setting can be change in the button display setting bar: 

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_104856.png)

The mode data display rate can be change in 2sec ~ 5 sec. The program will sample count and data percentile can also be changed from the drop down menu. 

Press the "Font Selection" button the font change window will pop-up: 

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_104908.png)

Check the "Synchronized Adjust" check box the [model] and [data] display will show the same change when user change one of the data display selection setting. 