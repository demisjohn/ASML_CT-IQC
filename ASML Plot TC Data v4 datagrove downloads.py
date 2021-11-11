# -*- coding: utf-8 -*-
"""

@author: demis

    
ASML Plot TC Data
    Plot the historical temperature data from ASL's TC/CTlogM8477.cur
    

    
"""

#################
#   Options

# optionally set a Minimum Date/Time to start at.  
#       Set to None to ignore.
import datetime
#MinDate = "2021-06-30"      # Format: "2021-07-22" for July 22nd, 2021
#MinTime = (0,0,0)      # Format: (16,30,0) for 16:30 (aka 4:30pm)
#mindate = datetime.datetime.combine( datetime.date.fromisoformat( MinDate ) , datetime.time( *MinTime ) )
mindate = datetime.datetime.now() - datetime.timedelta( days = 45 )
mindate = datetime.datetime.combine( mindate.date() , datetime.time( 0,0,0 ) )  # set to midnight
SaveFig = False;    # save the plot to a file?
WS_ymin = None; #21.8      # set to None for auto

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
import glob


folder = DataGrove_dir

if not folder[-1] == "/":
    folder = folder + "/"

TCFiles = glob.glob( folder + "*.cur.*" )    # find paths to each text file
TCFiles.extend(  glob.glob( folder + "*.old.*" )  )

               
IQCFiles = glob.glob( folder + "QICC.*" )
IQCFileZ = []
for i,f in enumerate(IQCFiles):
    if not "tgs" in f:
        # get rid of the .tgs files in the list
        IQCFileZ.append(f)
#print("IQCFIleZ", IQCFileZ )



ct = ASML_CT.ASML_CT( TCFiles )   # analyze the files
iqcdata = ct.add_IQC_files( IQCFileZ )
ct.iqc_analyze()



fig = ct.plot(   WS_ymin=WS_ymin, data=ct.df[  ct.df['DateTime'] >  mindate  ]   , SaveFig=SaveFig )




print('done.')



