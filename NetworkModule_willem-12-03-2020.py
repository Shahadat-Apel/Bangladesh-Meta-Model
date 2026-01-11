# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 13:14:45 2019

@author: shahadad
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
import TimeIndexFunctions as TF

class NetworkModuleClass():
    """
    A class used to represent a the network for the Bangladesh Metamodel

    Inputs from framework
    ------
    [None]

    Results to framework
    ----------
    discharge : pandas series with discharge of current timestep for each node
    waterlevel : pandas series with waterlevel of current timestep for each node
    tidalrange : pandas series with tidalrang of current timestep for each node

    Methods
    -------
    initialzeModuleforRun()
        reads the networkdefinition from file
        reads the boundary conditions 
            upstream discharge
            downstream waterlevels 
            downstream tidal range
        sets the initial values for the network values
    dotimestep(currentTimeIndex)
        updates discharge, waterlevel and tidalrange to contain the results for the currenttimestep
    postprocessing()
        currently does nothing
    """

    def __init__(self,datarootfolder):
        self._privatedatafolder =  os.path.join(datarootfolder,"PrivateData")
        self._privatedatafolder =  os.path.join(self._privatedatafolder,"NetworkModule")
        self._shareddatafolder = os.path.join(datarootfolder,"SharedData")

    def initializeModuleforRun(self, scenarionumber):
        
        # network distribution DataFrame
        self.scenario = scenarionumber
        if (self.scenario == 2) or (self.scenario ==4): #Ganges is working
            self._networkFileName = os.path.join(self._privatedatafolder,'Tables','Network_distribution_WithGanges.csv')
            self._network_df   = pd.read_csv(self._networkFileName, sep=',', index_col=None)
        else:
            self._networkFileName = os.path.join(self._privatedatafolder,'Tables','Network_distribution_WithoutGanges.csv')
            self._network_df   = pd.read_csv(self._networkFileName, sep=',', index_col=None)
        
        # upstream discharge DataFrame
        self._disch_file = os.path.join(self._privatedatafolder,'Tables','U_S_Boundaries.csv')
        self._disch_df   = pd.read_csv(self._disch_file, sep=',', index_col=0)
        self._disch_df.index = pd.to_datetime(self._disch_df.index, format="%d/%m/%Y %H:%M")
        # downstream water level DataFrame
        self._dsWL_file = os.path.join(self._privatedatafolder,'Tables','D_S_Boundaries.csv')
        self._dsWL_df   = pd.read_csv(self._dsWL_file, sep=',', index_col=0)
        self._dsWL_df.index = pd.to_datetime(self._dsWL_df.index, format="%d/%m/%Y %H:%M")
        
        if (self.scenario == 3) or (self.scenario == 4): # 1 meter sealevel rise
            self._dsWL_df = self._dsWL_df+1
        else:
            self._dsWL_df = self._dsWL_df
        # Tidal Range DataFrame
        self._tidalRange_file = os.path.join(self._privatedatafolder,'Tables','Tidal_Boundaries.csv')
        self._tidalRange_df   = pd.read_csv(self._tidalRange_file, sep=',', index_col=0)
        self._tidalRange_df.index = pd.to_datetime(self._tidalRange_df.index, format="%d/%m/%Y %H:%M")
        
        # Salinity DataFrame
        self._salinity_file = os.path.join(self._privatedatafolder,'Tables','Salinity_Boundaries.csv')
        #!!!!!!! Is the follwoing statement correct??????????????
        self._salinity_df   = pd.read_csv(self._tidalRange_file, sep=',', index_col=0)
        self._salinity_df.index = pd.to_datetime(self._tidalRange_df.index, format="%d/%m/%Y %H:%M")
        self._wlDataFrame = self._disch_df.copy()
        self._salinityDataFrame = self._disch_df.copy()
        # tidal range calculation
        # for row in self._network_df.iloc[::-1].iterrows():
        #     node_id   = row[1]['Node'] # River Node
        #     node_calc = row[1]['TidalCalc'] # Discharge distribution factor
        #     if node_id == node_calc:
        #         ts = self._tidalRange_df[node_id]
        #     else:
        #         calc = self._network_df [self._network_df.Node == node_id]['TidalCalc'].values
        #         if '*' in calc[0]:
        #             node_calc = calc[0].split('*')[0]
        #             factor    = calc[0].split('*')[1]
        #             ts = self._tidalRange_df[node_calc] * float(factor)
        #             self._tidalRange_df[str(node_id)] = ts
        #         # elif '+' in calc[0]:
        #         #     node_calc_1 = calc[0].split('+')[0]
        #         #     node_calc_2 = calc[0].split('+')[1]
        #         #     ts = self._tidalRange_df[node_calc_1] + self._tidalRange_df[node_calc_2]
        #         #     self._tidalRange_df[str(node_id)] = ts
        #         else:
        #             ts = self._tidalRange_df[node_calc]
        #             self._tidalRange_df[str(node_id)] = ts
        # make available all results of the first timestep as previous timestep for the water balance module
        self.dotimeStep(TF.datetotimeindex(dt.date(1985,1,1)))

    def _calculatedischargecurrenttimestep(self,currentTimeIndex):
        # discharge calculation
        currentdate =TF.timeindextodate(currentTimeIndex)
        self._df_dischargecurrenttimestep = self._disch_df.loc[currentdate]
        #print(self._df_dischargecurrenttimestep)

        for row in self._network_df.iterrows():
            node_id   = row[1]['Node'] # River Node
            node_calc = row[1]['DischargeCalc'] # Discharge distribution factor
            #print(node_calc, "1st")
            if node_id == node_calc:
                ts = self._df_dischargecurrenttimestep[node_id]
            else:
                calc = self._network_df[self._network_df.Node == node_id]['DischargeCalc'].values
                #print(calc, "2nd")
                counter = calc[0].count('+')
                if '*' in calc[0]:
                    node_calc = calc[0].split('*')[0]
                    factor    = calc[0].split('*')[1]
                elif counter==1:
                    node_calc_1 = calc[0].split('+')[0]
                    node_calc_2 = calc[0].split('+')[1]
                    ts = self._df_dischargecurrenttimestep[node_calc_1] + self._df_dischargecurrenttimestep[node_calc_2]
                elif counter==2:
                    node_calc_1 = calc[0].split('+')[0]
                    node_calc_2 = calc[0].split('+')[1]
                    node_calc_3 = calc[0].split('+')[2]
                    ts = self._df_dischargecurrenttimestep[node_calc_1] + self._df_dischargecurrenttimestep[node_calc_2]+ self._df_dischargecurrenttimestep[node_calc_3]
                else:
                    ts = self._df_dischargecurrenttimestep[node_calc]
                #print('node_id',node_id)
                #print('ts',ts)
                self._df_dischargecurrenttimestep[str(node_id)]=ts
                #print('dis',self._df_dischargecurrenttimestep)
        return()

    def _calculatewaterlevelscurrenttimestep(self,currentTimeIndex):
        # water level calculation
        currentdate =TF.timeindextodate(currentTimeIndex)
        self._df_waterlevelcurrenttimestep = self._wlDataFrame.loc[currentdate]
        for row in self._network_df.iterrows():
            node_idr   = row[1]['Node'] # River Node
            outletNode   = row[1]['OutletNode'] # water level dependened node
            rating_ho1   = row[1]['ho1'] # 1st Rating Curve WL = Node*d1+ ho1+ (Q/ao1)^n1 
            rating_a1 = row[1]['a1']
            rating_n1 = row[1]['n1']
            rating_d1 = row[1]['d1']
            rating_ho2   = row[1]['ho2'] #2nd Rating Curve WL = Node*d1+ ho1+ (Q/ao1)^n1
            rating_a2 = row[1]['a2']
            rating_n2 = row[1]['n2']
            rating_d2 = row[1]['d2'] #WaterLevelFactor
            waterLevelFactor = row[1]['WaterLevelFactor']
            Q_t = row[1]['Q_T'] # Discharge threshold value, it is defined the right H-Q relationship
            if self._df_dischargecurrenttimestep[str(node_idr)] < Q_t:
                rating_ho = rating_ho1
                rating_a = rating_a1
                rating_n = rating_n1
                rating_d = rating_d1
            else:    
                rating_ho = rating_ho2
                rating_a = rating_a2
                rating_n = rating_n2
                rating_d = rating_d2
            self._df_waterlevelcurrenttimestep[node_idr] = rating_d * self._dsWL_df.loc[currentdate][outletNode] +  (rating_ho + (self._df_dischargecurrenttimestep[node_idr]/rating_a)**(1/rating_n))*waterLevelFactor
        return()

    def _calculatesalinitycurrenttimestep(self,currentTimeIndex):
        #Salinity calculation
        currentdate =TF.timeindextodate(currentTimeIndex)
        self._df_salinitylevelcurrenttimestep = self._salinityDataFrame.loc[currentdate]
        for row in self._network_df.iterrows():
             node_idrs   = row[1]['Node'] # River Node
             outletNodes   = row[1]['OutletNode'] # water level dependened node
             sq1 = row[1]['sq1'] # salinity parameter
             sq2 = row[1]['sq2']
             swl1 = row[1]['swl1']
             swl2   = row[1]['swl2']
            
             #self._salinityDataFrame[node_idrs] = sq1*(self._disch_df[node_idrs]**sq2)*self._salinity_df[outletNodes]*swl1*(self._wlDataFrame[outletNodes]**swl2)
             #self._df_salinitylevelcurrenttimestep[node_idrs] = sq1*(self._df_dischargecurrenttimestep[node_idr][node_idrs]**sq2)*self._salinity_df[outletNodes]*swl1*(self._df_waterlevelcurrenttimestep[outletNodes]**swl2)
        
        return()
    
    def dotimeStep(self,currentTimeIndex):
        
        self._calculatedischargecurrenttimestep(currentTimeIndex)
        self.discharge = self._df_dischargecurrenttimestep
        self._calculatewaterlevelscurrenttimestep(currentTimeIndex)
        self.waterlevel = self._df_waterlevelcurrenttimestep
        try:
            # self.waterlevel = self._wlDataFrame.loc[dateCurrentTimeIndex]
            # self.tidalrange = self._tidalRange_df.loc[dateCurrentTimeIndex]
            # self.salinity = self._salinityDataFrame.loc[dateCurrentTimeIndex]
            errorCode =0
        except:
            errorCode =1
            
        return errorCode
            
    def postProssesing(self):
        self._wlDataFrame.to_csv(os.path.join(self._privatedatafolder,'Calibration\{}_wl.csv'.format(self.scenario)), sep=',',index=True) #"{}{}".format(s, y)
        self._disch_df.to_csv(os.path.join(self._privatedatafolder,'Calibration\{}_Q.csv'.format(self.scenario)), sep=',',index=True)
#        self._tidalRange_df.to_csv(os.path.join(self._privatedatafolder,'Calibration\{}_TR.csv'.format(self.scenario)), sep=',',index=True)
        pass





def main():
    print("Self Testing from network module")
    beginTime = dt.date(1985,1,1)
    endTime = dt.date(1985,1, 11)
    startTimeIndex = TF.datetotimeindex(beginTime)
    endTimeIndex = TF.datetotimeindex(endTime)
    #print(startTimeIndex, endTimeIndex)
    
    dataroot = os.getcwd()
    nmodule = NetworkModuleClass(dataroot)
    scenarioNumber = int(input("Enter Scenario Number : "))
    print(type(scenarioNumber) )
    
    nmdata = nmodule.initializeModuleforRun(scenarioNumber)

    global waterleveltimestep0
    global dischargetimestep0
#    waterleveltimestep0 = nmodule.waterlevel
#    dischargetimestep0 = nmodule.discharge
    #print(nmodule.wlDataFrame.head(5))

    for timeStepIndex in range(startTimeIndex, endTimeIndex):
        errorcode = nmodule.dotimeStep(timeStepIndex)
        if errorcode != 0:
            print('Error in dotimestep')
        #print(errorcode)
        if errorcode == 0:
            print(TF.timeindextodate(timeStepIndex),nmodule.waterlevel['N278'])
            
    nmodule.postProssesing()

    
if __name__ == "__main__":
    main()  


#self.disch_df.plot().legend(ncol=2, bbox_to_anchor=(.95, 0.55, 0.5, 0.5), loc='upper center', fontsize='small')
#self.disch_df.groupby(self.disch_df.index.month).mean().plot().legend(ncol=2, bbox_to_anchor=(.95, 0.55, 0.5, 0.5), loc='upper center', fontsize='small')
#plt.show()
