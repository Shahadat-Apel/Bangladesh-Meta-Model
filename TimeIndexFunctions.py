# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 06:42:02 2019

@author: Carthago
"""
import datetime as dt

def datetotimeindex(currentdate):  
    return (currentdate.year-1)*36+(currentdate.month-1)*3+min(2,( currentdate.day-1)//10)+1

def timeindextoyear(timestep):
    return (timestep-1)//36+1

def timeindextodecade(timestep):
    return ((timestep-1)%36)+1

def timeindextomonth(timestep):
    return ((timeindextodecade(timestep)-1)//3)+1

def timeindextodecadeinmonth(timestep):
    return ((timeindextodecade(timestep)-1)%3)+1

def timeindextodate(timestep):
    dec =timeindextodecadeinmonth(timestep)
    day=21
    if dec==1:
        day=1
    elif dec==2:
        day=11
    return dt.date(timeindextoyear(timestep),timeindextomonth(timestep),day)

    
