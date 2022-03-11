#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Module ASML_CT

Takes as arguments a list of filepaths, which should be the paths to CT/* datafiles.
Returns a Pandas Dataframe containing all the CT data.


Created on Wed Mar 17 18:20:17 2021

@author: Demis D. John
Univ. of California Santa Barbara; Nanofabrication Facility; Mar. 2021
"""


####################################################
# Options:
    
# Data options:
IQClimits = (-50,+50)  # nm, max/min acceptabel IQC





####################################################
# Module setup etc.

# from __future__ import division  # Fix nonsense division in Python2.x (where 1/2 = 0 )
import numpy as np  # NumPy (multidimensional arrays, linear algebra, ...)
import scipy as sp  # SciPy (signal and image processing library)

import matplotlib as mpl         # Matplotlib (2D/3D plotting library)
import matplotlib.pyplot as plt  # Matplotlib's pyplot: MATLAB-like syntax
#from pylab import *              # Matplotlib's pylab interface
#plt.ion()                            # Turned on Matplotlib's interactive mode

####################################################

import time     # for getting current date
import datetime # for converting string date/times
#import os
#import csv
import pandas as pd  # Data/database Manipulation
import matplotlib.dates as mdates #MatPlotLib date representation

####################################################


# show debugging output? (Default setting)
global asml_DEBUG
asml_DEBUG=False

def DEBUG():
    """ Return DEBUG boolean variable."""
    global asml_DEBUG
    return asml_DEBUG

def set_DEBUG():
    """ Turn on Debugging output. """
    global asml_DEBUG
    asml_DEBUG = True

def unset_DEBUG():
    """ Turn off Debugging output."""
    global asml_DEBUG
    asml_DEBUG = False
    
####################################################


class ASML_CT:
    """
    Analyze CT log files from ASML files system. Data is sorted by date & time.
    
    ASML_CT( files=[],  return_dataframe=True )
    
    Arguments
    ---------
    files: List of file paths (strings). 
    return_dataframe : {True | False}, defaults to True
        Return the combined, sorted dataframe
    
    
    Returns a dataframe with all the data loaded, also stores this internally in ASML_TCU.df
    
    Examples
    --------
    ASML_CT( ["/path/to/my/file/CTlogM8477 2021-03-17 1300.old",  "CTlogM8477.cur"] )
    ASML_CT.plot()
    DataFrame = ASML_CT.df   # do your own analysis with Pandas
    """
    
    
    
    def __init__(self, files=[] ):
        """ see help(ASML_TCU) for constructor info"""
        self.files = files
        self.Dates = []
        # self.iqc = None;  Unused?
        self.df =  self.analyze()
        self.iqc_files = []
    #end __init__()

    def analyze(self):
        """
        Run the analysis on the datafiles, return a DataFrame with all data loaded.
        """
        #print('Running...')
        
        ## Headers:
        # time     Tlens  Twater Tair   Tws    Ttcu   Ftcu   Tact   Pairin Pgas    Plens  Flens  Cont   Hum s   
        self.columns=["Tlens",  "Twater", "Tair",   "Tws",    "Ttcu",   "Ftcu",   "Tact",   "Pairin", "Pgas",    "Plens",  "Flens", "Cont", "Hum"]
        self.units = ["°C",     "°C",     "°C",     "°C",     "°C",     "l/min",  "°C",   "Pascal", "bar x 10^5","bar x 10^5","l/hr", "",   "%"]
        ## Data:
        # 00:01:55 22.007 21.999 18.849 22.023 22.080 42.87  22.070 1067   796026  101985 6.16   off    0  
        
        
        
        Data = []
        #self.Dates = []
        CurDate = datetime.date(2020,1,1) # initialize variable with arbitrary date/time
        CurTime = datetime.time(0,0,0)
        for curfile in self.files:
            if DEBUG(): print("opening file:", curfile)
            line=True
            with open(curfile, "rU") as f:
                while line:
                    line = f.readline()
                    if not line: 
                        if DEBUG(): print("Done with file:", curfile)
                        break  # end when EOF (blank string returned)
                    #print(line)
                    try: 
                        #print("trying: float(%s)" % str( line.strip()[0:2] ) )
                        float( line.strip()[0:2] ) # test if next data starts with a number
                    except ValueError:
                        # line is not nnumeric, get the Date
                        if line.strip() == "Initialize":
                            f.readline() # the machine number - discard
                            line = f.readline()
                            FullLine = line  # store for debugging only
                        # Get the date; date format:
                        # TUE MAR 09 13:08:26 2021
                        line = line[4:-1]   # strip the 4 character day of week
                        #print("Date: `%s`" % line);
                        try:
                            dateobj = datetime.datetime.strptime( line, '%b %d %H:%M:%S %Y')
                        except ValueError:
                            print("**>> Failed DateTime parsing on File: `%s`\n"%curfile, "FullLine read was:\n\t%s\n"%FullLine, "Parsed Line was:\n\t%s"%line)
                        CurDate = dateobj.date()
                        self.Dates.append(CurDate)
                        if DEBUG(): print("\t Found CT date+time:", dateobj, "\t Adding Date: ", self.Dates[-1])
                        for i in range(3):
                            line=f.readline()    # skip next three lines
                            #print("skipping line:", line)
                        line = f.readline()
                    #end try( numeric )
                    
                    if not line: break  # end when EOF (blank string returned)
                    
                    # Parse the data line:
                    CurTime = datetime.datetime.strptime( line[0:8], '%H:%M:%S').time()
                    
                    Tlens,  Twater, Tair,   Tws,    Ttcu,   Ftcu,   Tact,   Pairin, Pgas,    Plens,  Flens, Cont, Hum = \
                        float(line[9:15]), float(line[16:22]), float(line[23:29]), float(line[30:36]), float(line[37:43]), \
                        float(line[44:49]), float(line[51:57]), float(line[58:62]), float(line[65:71]), float(line[73:79]), \
                        float(line[80:84]), line[87:91], line[94:95]
                    Data.append(  [datetime.datetime.combine(CurDate, CurTime), Tlens,  Twater, Tair,   Tws,    Ttcu,   Ftcu,   Tact,   Pairin, Pgas,    Plens,  Flens, Cont, Hum]  )
                    #print("CurTime = ", CurTime)
                    #print( Tlens,  Twater, Tair,   Tws,    Ttcu,   Ftcu,   Tact,   Pairin, Pgas,    Plens,  Flens, Cont, Hum)
                    
                    
                    #end if(first data Frame)
                    
                    
                  #x, y = line[:28], line[29:]
                #end while(line) - ends at EOF
            #end with(file)
        #end for(files)
        
        
        df = pd.DataFrame(  Data, columns=["DateTime", *self.columns]  )
        df = df.sort_values("DateTime")
        
        self.data = df
        return self.data
    #end analyze()
    
    
    def plot(  self, SaveFig=False, prefix="", data=None, IQCdata=None, PlotTemperature=True, PlotPressure=False, PlotSupplyGas=False, PlotTCU=False, WS_ymin=None, WS_ymax=None, ax1args=dict(), ax2args=dict(), ax3args=dict(),  figargs=dict()  ):
        """
        Plot the temperature data. If IQC data has been analyzed, plot that as well.
        Multiple MatPLotLib Axes objects are plotted as so:
            ax1 is Lens (Tlens) & Wafer Stage (Tws) temps.
            ax2 is Incoming Air (Tair) temp.
            ax3 is IQC data, if IQC data has been imported with `ASML_CT.add_IQC_dir()`.

        Parameters
        ----------
        SaveFig : {True | False}, defaults to False
            Save the figure to a file?
        
        prefix : string, defaults to ""
            Optional prefix to filename, could be a file path. Only used if SaveFig is enabled.
        
        data, IQCdata : pandas.DataFrame, defaults to full DataFrame acquired from files.
            Optionally filter or mainpulate the DataFrame for plotting.
            eg. Plot only data newer than 2021-03-11:
                mindate = datetime.datetime.combine( datetime.date.fromisoformat('2021-03-11') , datetime.time(0,0,0) )
                MyCTobj.plot(   data=ct.df[  ct.df['DateTime'] >  mindate  ]    )
            
            
        PlotTemperature : {True|False}, optional
            Add a plot for Temperature data?  Defaults to True.
            Plots "Incoming Air", "Wafer Stage Air" and "Lens" Temperatures.
        
        PlotLensPressure : {True|False}, optional
            Add a plot for Pressure data?  Defaults to False.
            Plots "Lens Presure" on it's own axis.
        
        PlotLensPressure : {True|False}, optional
            Add a plot for Pressure data?  Defaults to False.
            Plots "Lens Presure" on it's own axis.
        
        PlotSupplyGas : {True|False}, defualts to False
            If plotting presure, also plot supply gas?
        
        PlotTCU : {True|False}, defaults to False
            Add a plot of TCU temp?
        
        WS_ymin : float, defaults to None
            Y minimum for Wafer Stage axis, Default of `None` means automatic.  21.8      # set to None for auto
        
        WS_ymax : float, defaults to None
            Y maximum for Wafer Stage axis, Default of `None` means automatic.  21.8      # set to None for auto
        
        figargs, ax1args, ax2args, ax3args : Dictionary
            Dictionary of arguments to pass to the plot commands of the Matplotlib.pyplot.subplots() command, and ax1/ax2/ax3.plot() commands, respectively.
        
        Returns
        -------
        Fig : Matplotlib Figure object containing the Axis objects.
            

        """
        if isinstance(data, type(None)): data = self.data
        
        iqcplot = False
        if isinstance(IQCdata, type(None)): 
            try: 
                iqcdata = self.iqcdata
                iqcplot = True
            except AttributeError:
                if DEBUG(): print("No IQC data")
            #end try
        else:
            iqcdata = IQCdata
            icqplot=True
        #end if(IQCdata)
        
        
        # ax1+ax2 is temperature data, ax3 is IQC data, ax4 is Pressure data
        if (not iqcplot) and (not PlotPressure):
            fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1, sharex=True, **figargs)
        elif (iqcplot) and (not PlotPressure):
            fig, [ax2, ax1, ax3] = plt.subplots(nrows=3, ncols=1, sharex=True, **figargs)
        elif (not iqcplot) and (PlotPressure):
            fig, [ax2, ax1, ax4] = plt.subplots(nrows=3, ncols=1, sharex=True, **figargs)
        elif (iqcplot) and (PlotPressure) and not PlotSupplyGas:
            fig, [ax2, ax1, ax3, ax4, ax5] = plt.subplots(nrows=5, ncols=1, sharex=True, **figargs)
        elif (iqcplot) and (PlotPressure) and PlotSupplyGas:
            fig, [ax2, ax1, ax3, ax4, ax5, ax6] = plt.subplots(nrows=6, ncols=1, sharex=True, **figargs)
        #end if(which plots)
        
        
        # Ax1: Incoming Air
        ax1.plot(   data["DateTime"], data["Tlens"], label="Lens"   , **ax1args) 
        ax1.plot(   data["DateTime"], data["Tws"], label="WaferStage Air"     , **ax2args) 
        if PlotTCU: ax1.plot(   data["DateTime"], data["Ttcu"], label="TCU Temp."     , **ax2args) 
        
        
        # Format Plots:
            
        uDates = np.unique(   [ x.date() for x in data["DateTime"] ]   )
        
        if WS_ymin:
            ymin = WS_ymin
        else:
            ymin = ax1.get_ylim()[0]
        #end if(WS_ymin)
        
        if WS_ymax:
            ymax = WS_ymax
        else:
            ymax = ax1.get_ylim()[1]
        #end if(WS_ymax)
        
        ax1.set_ylim(ymin, ymax)
        ax1.set_xticks(uDates, minor=True)
        ax1.xaxis.grid(True, which='major')
        ax1.xaxis.grid(True, which='minor')
        #ax1.vlines( self.Dates , color="grey", alpha=0.05, ymin=ax1.get_ylim()[0], ymax=ax1.get_ylim()[1] )
        #if DEBUG(): print( "Ax1: Ylims: ", ax1.get_ylim()[0], ax1.get_ylim()[1] )
        ax1.legend()
        ax1.set_ylabel("°C")
        
        # Ax2: WS + Lens
        ax2.plot(   data["DateTime"], data["Tair"], label="Incoming Air", **ax3args   )
        ax2.set_xticks(uDates, minor=True)
        ax2.xaxis.grid(True, which='major')
        ax2.xaxis.grid(True, which='minor')
        #ax2.vlines( self.Dates , color="grey", alpha=0.05, ymin=ax2.get_ylim()[0], ymax=ax2.get_ylim()[1] )
        ax2.legend()
        ax2.set_ylabel("°C")
        
        bottom_axis = ax2
        
        # Ax3: IQC Focus
        if iqcplot:
            # restrict IQC data to the date ranges  in Temperature data.
            tempmin, tempmax = data.DateTime.min() , data.DateTime.max() + datetime.timedelta(hours=6) # add 6 hours, to ensure latest IQC run is included (since TC data is intermittent).
            if DEBUG(): print("Temp. Data min/max:\n", tempmin, tempmax  )
            iqcplotdata = iqcdata[  iqcdata.DateTime.between(tempmin, tempmax, inclusive=True)  ].sort_values("DateTime")
            if DEBUG(): print("IQC Data, DateTime:\n", iqcplotdata.DateTime)
            
            ax3.plot(   iqcplotdata["DateTime"], iqcplotdata["IQCfoc"], label="Manual IQC Verify", marker="x", **ax3args   )
            
            # shade acceptable IQC range
            # Create rectangle x coordinates
            startTime = tempmax + datetime.timedelta(days=14)
            endTime = tempmin - datetime.timedelta(days=14)
            
            # convert to matplotlib date representation
            start = mdates.date2num(startTime)
            end = mdates.date2num(endTime)
            rectwidth = end - start
            
            ax3.add_artist(   plt.Rectangle( (start,IQClimits[0]), rectwidth, (IQClimits[1]-IQClimits[0]), alpha=0.1, zorder=1, color="green")   )

            
            ax3.set_xticks(uDates, minor=True)
            ax3.xaxis.grid(True, which='major')
            ax3.xaxis.grid(True, which='minor')
            #ax3.vlines( self.Dates , color="grey", alpha=0.05, ymin=ax3.get_ylim()[0], ymax=ax3.get_ylim()[1] )
            ax3.legend()
            ax3.set_ylabel("Focus Correction (nm)")
            
            bottom_axis = ax3
        
        
        # Ax4: Pressure data
        if PlotPressure:
            if DEBUG(): print("--> Pressure Plot")
            ax4.plot(   data["DateTime"], np.array(data["Plens"])/1e5, label="Lens Pressure", **ax3args   )
            ax4.set_xticks(uDates, minor=True)
            ax4.xaxis.grid(True, which='major')
            ax4.xaxis.grid(True, which='minor')
            ax4.legend()
            ax4.set_ylabel("Bar")
            
            ax5.plot(   data["DateTime"], np.array(data["Pairin"]), label="Incoming Air Pressure", **ax3args   )
            ax5.set_xticks(uDates, minor=True)
            ax5.xaxis.grid(True, which='major')
            ax5.xaxis.grid(True, which='minor')
            ax5.legend()
            ax5.set_ylabel("Pascal")
            
            if PlotSupplyGas:
                ax6.plot(   data["DateTime"], np.array(data["Pgas"])/1e5, label="Supply Gas", **ax3args   )
                ax6.set_xticks(uDates, minor=True)
                ax6.xaxis.grid(True, which='major')
                ax6.xaxis.grid(True, which='minor')
                ax6.legend()
                ax6.set_ylabel("Bar")
                
                bottom_axis = ax6
        #end if(Pressure)
            
        
        for tl in bottom_axis.get_xticklabels():
            #print(dir(tl))
            tl.set_rotation(-90)
        
        
        #df.plot(x="DateTime", y=["Tair", "Tws", "Tlens"] )
        fig.tight_layout()
        plt.show()
        
        if SaveFig: 
            TodayDate = time.strftime("%Y-%m-%d %H.%M.%S")           # Get current date and time as string
            fig.savefig(str(prefix) + 'ASML CT Temps - ' + TodayDate + '.png')
        
        return fig
    #end plot()

    
    def add_IQC_dir(self, folder="/path/to/QICC/Data" ):
        """
        Add IQC/QICC data, from QICC files in a folder.  
        Pass a string that is the path to the folder.
        

        Parameters
        ----------
        dir : string
            Path to the directory containing QICC data files. 

        Returns
        -------
        None.

        """
        
        
        #import sys, os, os.path         # OS-specific path manipulations, sys.exit(), terminal interaction (stout etc.)
        import glob     # filename matching etc.
        #import re       # RegEx matching
        #import pandas as pd   # Database module
        import datetime    # date+time objects
        
        Fol = folder
        self.iqc_folder = folder
        
        if not folder[-1] == "/":
            folder = folder + "/"
        
        AllFiles = glob.glob( Fol + "*" )    # find paths to each text file
        
        #print(AllFiles)
        
        
        # Find file extensions with numbers, eg. "QICC.32"
        DataFiles=[]
        for f in AllFiles:
            #print( f[-4: ] )
            if  f[-2: ].isdecimal():
                # add only filenames ending in numbers
                DataFiles.append(f)
        #end for(AllFiles)
        
        #print(DataFiles)
        
        self.iqc_files.extend(DataFiles)
    #end add_IQC_dir()    
    
        
    def add_IQC_files(self, FilePaths):
        """
        Add IQC/QICC data, from QICC files specified.  
        Pass a string, or list of strings, that are the path(s) to the file(s).
        

        Parameters
        ----------
        FilePaths : string, or iterable containing strings
            List of string Paths to the QICC data file(s). 

        Returns
        -------
        None.

        """
        
        if isinstance(FilePaths, str):  
            FilePaths = [FilePaths]
        
        for F in FilePaths:
            self.iqc_files.append(F)
        
    #edn add_IQC_files()
        
        
    def iqc_analyze(self):
        '''
        Analyzes QICC data files to extract measured IQC Focus Correction, and Date/Time of measurement.
        IQC data points and plots will be added to the asml_ct object.

        Parameters
        ----------
        No arguments, uses internal variables set by
        ASML_TC.iqc_addfolder(), or
        ASML_TC.iqc_add_files()

        Returns
        -------
        None.
        '''
        
        DataFiles = self.iqc_files
        
        ## Parse each file
        # Line, Col, length within the text file
        datepat = [1,54,10]  
        timepat = [1,71,5]
        focpat =  [37,40,9]
        
        df = pd.DataFrame( columns=["DateTime","IQCfoc"] )
        for curfile in DataFiles:
            AllLines=[]
            line=True
            with open(curfile, "r") as f:
                while line:
                    line = f.readline()
                    if not line: 
                        if DEBUG(): print("Done with file:", curfile)
                        break  # end when EOF
                    AllLines.append( line + "\n" )
                #end while(file)
            #end with(curfile)
            
            DateStr = AllLines[ datepat[0] ][ datepat[1]:datepat[1]+datepat[2] ]
            #print(DateStr)
            TimeStr = AllLines[ timepat[0] ][ timepat[1]:timepat[1]+timepat[2] ]
            #print(TimeStr)
            dateobj = datetime.datetime.strptime( DateStr+" "+TimeStr, '%m/%d/%Y %H:%M')
            IQCfoc = float( AllLines[ focpat[0] ][ focpat[1]:focpat[1]+focpat[2] ] )
            if DEBUG(): print(dateobj, "\t", IQCfoc)
            
            
            # add data to the end of DataFrame
            df.loc[ len(df) ] = [dateobj, IQCfoc]
            
        #end for(DataFiles)
        self.iqcdata = df
        return self.iqcdata
    #end add_IQC_dir()
    
    def export_data(self, outfile='', Excel=True, IQCdata=False, CSV=False):
        '''Export all data in the class to a comma-delimited text file, by defualt sorted by date/time.
        
        outfile : string,
            String of path/filename to output to.  File extension ".csv" will be appended.
            If left empty, then a current date/time timestamp will be used.
        
        Excel: {True|False}, defaults to True
            Output an Excel file?
        
        CSV : {True|False}, defaults to False
            Output a CSV file?
        
        IQCdata : {True|False}, False by default
            Also export IQC data?  Will generate a separate *.iqcdata text file.
        
        '''
        
        if IQCdata: raise NotImplementedError("IQC Data export not yet implemented")
        
        if outfile == '':
            '''If no output filename was given, use timestamp'''
            import datetime
            outfile = "ASML CT Data " + datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        
        
        if (not CSV) and (not Excel): raise ValueError("No output specified. Set either CSV or Excel argument to True.")
        if CSV:
            f = outfile+".csv"
            self.data.to_csv( f )
            print( "CSV File saved to: `%s`"%(f) )
        if Excel:
            f = outfile+".xlsx"
            self.data.to_excel( f )
            print( "Excel File saved to: `%s`"%(f) )
        #end if(CSV/Excel)
            
        
    #end export_data()
    
    # function aliases:
    IQC = add_IQC_dir
    
#end class(ASML_TCU)