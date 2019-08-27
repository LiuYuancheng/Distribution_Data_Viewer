# Distribution_Data_Viewer

##### This project will create a distribution data viewer to show the experiment result of the netFetcher.(Load all the experiment CSV file and create the distribution curve.)

 

| The data viewer will show 6types of file transfer delay data which collected by the netFetcher program: |
| ------------------------------------------------------------ |
| Type 0: Timestamping Delay                                   |
| Type 1: Preprocessing Delay                                  |
| Type 2: Disk Seek Delay                                      |
| Type 3: Disk Read Delay                                      |
| Type 4: Client Observed Delay                                |
| Type 5: Input/Output Delay (Type 2 + Type 3)                 |

---
###### User interface and display mode: 

The distribution data viewer has 2 display mode: **Parallel display mode** and  **Compare display mode**

Parallel display mode:

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_102527.png)

Compare display mode:

![](https://github.com/LiuYuancheng/Distribution_Data_Viewer/blob/master/misc/2019-08-27_102419.png)

This is the cmd to install 

[wxPython]: https://wxpython.org/pages/downloads/index.html: 

```
pip install -U wxPython
```

This is the cmd to install 

[numpy]: https://pypi.org/project/numpy/

[ ] :

```
pip install numpy
```

(The numpy should be auto-installed when you installed the wxpython)

To run the program, go/cd to the src folder and run the "distributionViewer.py" program by:

python distributionViewer.py

The tested data CSV files are in the 'data' and 'model' folder.
