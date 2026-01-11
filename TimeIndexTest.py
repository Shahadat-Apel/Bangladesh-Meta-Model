# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 06:42:02 2019

@author: Carthago
"""
import datetime as dt
import TimeIndexFunctions as tif

start_date = dt.date(2013, 1, 1)
end_date = dt.date(2015, 6, 11)

start_timestep=tif.datetotimeindex(start_date)
index =tif.datetotimeindex(end_date)
print(start_timestep)
print(tif.datetotimeindex(end_date))
print(tif.datetotimeindex(end_date)-tif.datetotimeindex(start_date))
print(tif.timeindextodecade(index))
print(tif.timeindextomonth(index))
print(tif.timeindextodecadeinmonth(index))
print(tif.timeindextoyear(index))

#for timestep in range(tif.datetotimeindex(start_date), tif.datetotimeindex(end_date)):    
#    print(timestep,tif.timeindextodate(timestep))
