# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 13:14:45 2019

@author: 
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
import TimeIndexFunctions as TF

class DummyWaterBalanceClass():
    def __init__(self,datarootfolder):
        privatedatafolder =  os.path.join(datarootfolder,"PrivateData")
        self._privatedatafolder =  os.path.join(privatedatafolder,"DummyWaterBalanceModuleWD")
        self.shareddatafolder = os.path.join(datarootfolder,"SharedData")

    def initializeModuleforRun(self):
        #calculate the cropping pattern per upzaila (544), landtype (5) and crop (15)
       
        upzFileName = os.path.join(self._privatedatafolder,'Tables','Upazila.csv')
        df_upazila   = pd.read_csv(upzFileName, sep=',', index_col=None)
        nupz= len(df_upazila)
        upzPrecipitationFileName=os.path.join(self._privatedatafolder,'Tables','Upz_P.csv')
        self._df_upzPrecipitation = pd.read_csv(upzPrecipitationFileName, sep=',',index_col=0)
        self._df_upzPrecipitation.index.name='timeindex'
        self._df_upzPrecipitation.index=list(map(TF.timeindextodate, self._df_upzPrecipitation.index))
        print(self._df_upzPrecipitation.head(5))
        return 
        
    def dotimeStep(self,currentTimeIndex):
        #calculate the PET in m3/decade per upazila, per landtype, per crop
        #print(currentTimeIndex)
        self.upazilaPrec=self._df_upzPrecipitation.loc[currentTimeIndex]
            
    def postProssesing(self):
        pass





def main():
    #print("Self Testing Dummy Water Balance module")
    dataroot = os.getcwd()
    
    dummywaterbalance = DummyWaterBalanceClass(dataroot)
    beginTime = dt.date(1985,1,1)
    endTime = dt.date(1985,1, 21)
    startTimeIndex = TF.datetotimeindex(beginTime)
    endTimeIndex = TF.datetotimeindex(endTime)
    #print(startTimeIndex, endTimeIndex)
    
    code = dummywaterbalance.initializeModuleforRun();
# =============================================================================
#     for timeStepIndex in range(startTimeIndex, endTimeIndex):
#         dateCurrentTimeIndex =TF.timeindextodate(timeStepIndex)
#         dummywaterbalance.dotimeStep(timeStepIndex)
#         print(dummywaterbalance.upazilaPrec)
# 
# =============================================================================
           
if __name__ == "__main__":
    main()  

