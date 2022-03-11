# -*- coding: utf-8 -*-
"""

@author: demis

    
ASML Plot TC Data
    Plot the historical temperature data from ASML's TC/CTlogM8477.cur
    

    
"""

#################
#   Options

# optionally set a Minimum Date/Time to start at.  
#       Set to None to ignore.
import datetime
#MinDate = "2021-06-30"      # Format: "2021-07-22" for July 22nd, 2021
#MinTime = (0,0,0)      # Format: (16,30,0) for 16:30 (aka 4:30pm)
#mindate = datetime.datetime.combine( datetime.date.fromisoformat( MinDate ) , datetime.time( *MinTime ) )

mindate = datetime.datetime.now() - datetime.timedelta( days = 7 )  # plot data in the last 45 days, for example
mindate = datetime.datetime.combine( mindate.date() , datetime.time( 0,0,0 ) )  # set to midnight
SaveFig = True;    # save the plot to a file?
WS_ymin = None; #21.8      # set to None for auto
PlotPressure = False
PlotTCU = False
ExportData  = False

Headless = True  # running without a monitor
if Headless:
    import matplotlib
    matplotlib.use('Agg')
#end Headless

'''
# manually add TC .cur and .old files:
files = [
    "/Users/demis/Documents/Characterizations, Tools, Equipment, Experiments etc./Stepper #3 ASML/Error Logs and Batch_Reports/Temperature + IQC Logs/Temperature (TC) Logs/CTlogM8477 2021-07-21 1002.cur",
    "/Users/demis/Documents/Characterizations, Tools, Equipment, Experiments etc./Stepper #3 ASML/Error Logs and Batch_Reports/Temperature + IQC Logs/Temperature (TC) Logs/CTlogM8477 2021-07-21 1002.old",
    ]
'''


# automatically load TC + IQC files, eg. from DataGrove download:
DataGrove_dir="/Users/demis/Documents/Characterizations, Tools, Equipment, Experiments etc./Stepper #3 ASML/Error Logs and Batch_Reports/Temperature + IQC Logs/DataGrove logs (CT and ICQ)/"





####################################################
# Module setup etc.

#import numpy as np  # NumPy (multidimensional arrays, linear algebra, ...)
#import scipy as sp  # SciPy (signal and image processing library)

#import matplotlib as mpl         # Matplotlib (2D/3D plotting library)
#import matplotlib.pyplot as plt  # Matplotlib's pyplot: MATLAB-like syntax
#from pylab import *              # Matplotlib's pylab interface
#plt.ion()                            # Turned on Matplotlib's interactive mode

####################################################

print('Running...')

import ASML_CT
import datetime
import glob  #file path acquisition
import os # file date acquisition
import numpy


## Find files to analyze ##
folder = DataGrove_dir

if not folder[-1] == "/":
    folder = folder + "/"

TCFiles = glob.glob( folder + "*.cur.*" )    # find paths to each text file
TCFiles.extend(  glob.glob( folder + "*.old.*" )  )

# filter out files by creation date.
TCctime = [  datetime.datetime.fromtimestamp(  os.path.getctime(f)  ) for f in TCFiles]
TCctime_i = numpy.where(numpy.array(TCctime) >= mindate)[0]
TCFiles = numpy.array(TCFiles)
TCFiles = TCFiles[TCctime_i].tolist()


               
IQCFiles = glob.glob( folder + "QICC.*" )
IQCFileZ = []
for i,f in enumerate(IQCFiles):
    if not "tgs" in f:
        # get rid of the .tgs files in the list
        IQCFileZ.append(f)
#print("IQCFIleZ", IQCFileZ )

# filter out files by date.
IQCctime = [  datetime.datetime.fromtimestamp(  os.path.getctime(f)  ) for f in IQCFileZ]  
IQCctime_i = numpy.where(numpy.array(IQCctime) >= mindate)[0]
IQCFileZ = numpy.array(IQCFileZ)
IQCFileZ = IQCFileZ[IQCctime_i].tolist()


#raise UserError()


ASML_CT.unset_DEBUG()
ct = ASML_CT.ASML_CT( TCFiles )   # analyze the files
iqcdata = ct.add_IQC_files( IQCFileZ )
ct.iqc_analyze()




fig = ct.plot(   data=ct.df[  ct.df['DateTime'] >  mindate  ]   , PlotPressure=PlotPressure, WS_ymin=WS_ymin,  SaveFig=SaveFig, PlotTCU=PlotTCU )
if ExportData: ct.export_data()



print('done.')



