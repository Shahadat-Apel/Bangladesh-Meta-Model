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

    def initializeModuleforRun(self, scenarios):
        
        # network distribution DataFrame
        if (scenarios == 2) or (scenarios ==4): #Ganges is working
            self._networkFileName = os.path.join(self._privatedatafolder,'Tables\\Network_distribution_WithGanges.csv')
            self._network_df   = pd.read_csv(self._networkFileName, sep=',', index_col=None)
        else:
            self._networkFileName = os.path.join(self._privatedatafolder,'Tables\\Network_distribution_WithoutGanges.csv')
            self._network_df   = pd.read_csv(self._networkFileName, sep=',', index_col=None)
        
        # upstream discharge DataFrame
        self._disch_file = os.path.join(self._privatedatafolder,'Tables\\U_S_Boundaries.csv')
        self._disch_df   = pd.read_csv(self._disch_file, sep=',', index_col=0)
        self._disch_df.index = pd.to_datetime(self._disch_df.index, format="%d/%m/%Y %H:%M")
        # downstream water level DataFrame
        self._dsWL_file = os.path.join(self._privatedatafolder,'Tables\D_S_Boundaries.csv')
        self._dsWL_df   = pd.read_csv(self._dsWL_file, sep=',', index_col=0)
        self._dsWL_df.index = pd.to_datetime(self._dsWL_df.index, format="%d/%m/%Y %H:%M")
        
        if (scenarios == 3) or (scenarios == 4): # 1 meter sealevel rise
            self._dsWL_df = self._dsWL_df+1
        else:
            self._dsWL_df = self._dsWL_df
        # Tidal Range DataFrame
        self._tidalRange_file = os.path.join(self._privatedatafolder,'Tables\Tidal_Boundaries.csv')
        self._tidalRange_df   = pd.read_csv(self._tidalRange_file, sep=',', index_col=0)
        self._tidalRange_df.index = pd.to_datetime(self._tidalRange_df.index, format="%d/%m/%Y %H:%M")
        
        # Salinity DataFrame
        self._salinity_file = os.path.join(self._privatedatafolder,'Tables\Salinity_Boundaries.csv')
        self._salinity_df   = pd.read_csv(self._tidalRange_file, sep=',', index_col=0)
        self._salinity_df.index = pd.to_datetime(self._tidalRange_df.index, format="%d/%m/%Y %H:%M")
        # discharge calculation
        for row in self._network_df.iterrows():
            node_id   = row[1]['Node'] # River Node
            node_calc = row[1]['DischargeCalc'] # Discharge distribution factor
            if node_id == node_calc:
                ts = self._disch_df[node_id]
            else:
                calc = self._network_df [self._network_df .Node == node_id]['DischargeCalc'].values
                if '*' in calc[0]:
                    node_calc = calc[0].split('*')[0]
                    factor    = calc[0].split('*')[1]
                    ts = self._disch_df[node_calc] * float(factor)
                    self._disch_df[str(node_id)] = ts
                elif '+' in calc[0]:
                    node_calc_1 = calc[0].split('+')[0]
                    node_calc_2 = calc[0].split('+')[1]
                    ts = self._disch_df[node_calc_1] + self._disch_df[node_calc_2]
                    self._disch_df[str(node_id)] = ts
                else:
                    ts = self._disch_df[node_calc]
                    self._disch_df[str(node_id)] = ts
        # water level calculation
        self._wlDataFrame = self._disch_df.copy()
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
            self._wlDataFrame[node_idr][self._wlDataFrame[node_idr]<=Q_t] = rating_d1* self._dsWL_df[outletNode] +  rating_ho1 + (self._wlDataFrame[node_idr]/rating_a1)**(1/rating_n1)*waterLevelFactor
            self._wlDataFrame[node_idr][self._wlDataFrame[node_idr]>Q_t] = rating_d2* self._dsWL_df[outletNode]+ rating_ho2 + (self._wlDataFrame[node_idr]/rating_a2)**(1/rating_n2)*waterLevelFactor
        #Salinity calculation
        self._salinityDataFrame = self._disch_df.copy()
        for row in self._network_df.iterrows():
            node_idrs   = row[1]['Node'] # River Node
            outletNodes   = row[1]['OutletNode'] # water level dependened node
            sq1 = row[1]['sq1'] # salinity parameter
            sq2 = row[1]['sq2']
            swl1 = row[1]['swl1']
            swl2   = row[1]['swl2']
            
            self._salinityDataFrame[node_idrs] = sq1*(self._disch_df[node_idrs]**sq2)*self._salinity_df[outletNodes]*swl1*(self._wlDataFrame[outletNodes]**swl2)
           
        
        # tidal range calculation
        for row in self._network_df .iloc[::-1].iterrows():
            node_id   = row[1]['Node'] # River Node
            node_calc = row[1]['TidalCalc'] # Discharge distribution factor
            if node_id == node_calc:
                ts = self._tidalRange_df[node_id]
            else:
                calc = self._network_df [self._network_df.Node == node_id]['TidalCalc'].values
                if '*' in calc[0]:
                    node_calc = calc[0].split('*')[0]
                    factor    = calc[0].split('*')[1]
                    ts = self._tidalRange_df[node_calc] * float(factor)
                    self._tidalRange_df[str(node_id)] = ts
                elif '+' in calc[0]:
                    node_calc_1 = calc[0].split('+')[0]
                    node_calc_2 = calc[0].split('+')[1]
                    ts = self._tidalRange_df[node_calc_1] + self._tidalRange_df[node_calc_2]
                    self._tidalRange_df[str(node_id)] = ts
                else:
                    ts = self._tidalRange_df[node_calc]
                    self._tidalRange_df[str(node_id)] = ts
            

    def dotimeStep(self,currentTimeIndex):
        
        dateCurrentTimeIndex =TF.timeindextodate(currentTimeIndex)
        try:
            self.discharge = self._disch_df.loc[dateCurrentTimeIndex]
            self.waterlevel = self._wlDataFrame.loc[dateCurrentTimeIndex]
            self.tidalrange = self._tidalRange_df.loc[dateCurrentTimeIndex]
            self.salinity = self._salinityDataFrame.loc[dateCurrentTimeIndex]
            errorCode =0
        except:
            errorCode =1
            
        return errorCode
            
    def postProssesing(self):
        pass





def main():
    print("Self Testing from NW module")
    beginTime = dt.date(1985,1,1)
    endTime = dt.date(1985,5, 21)
    startTimeIndex = TF.datetotimeindex(beginTime)
    endTimeIndex = TF.datetotimeindex(endTime)
    #print(startTimeIndex, endTimeIndex)
    
    dataroot = os.getcwd()
    nmodule = NetworkModuleClass(dataroot)
    scenarioName = int(input("Enter Scenario Name : "))
    print(type(scenarioName) )
    
    nmdata = nmodule.initializeModuleforRun(scenarioName)
    #print(nmodule.wlDataFrame.head(5))
    nmodule._wlDataFrame.to_csv(os.path.join(nmodule._privatedatafolder,'Calibration\{}_wl.csv'.format(scenarioName)), sep=',',index=True) #"{}{}".format(s, y)
    nmodule._disch_df.to_csv(os.path.join(nmodule._privatedatafolder,'Calibration\{}_Q.csv'.format(scenarioName)), sep=',',index=True)
    nmodule._tidalRange_df.to_csv(os.path.join(nmodule._privatedatafolder,'Calibration\{}_TR.csv'.format(scenarioName)), sep=',',index=True)
    
    for timeStepIndex in range(startTimeIndex, endTimeIndex):
        errorcode = nmodule.dotimeStep(timeStepIndex)
        #print(errorcode)
        if errorcode == 0:
            print(TF.timeindextodate(timeStepIndex),nmodule.waterlevel['N278'])

    
if __name__ == "__main__":
    main()  


#self.disch_df.plot().legend(ncol=2, bbox_to_anchor=(.95, 0.55, 0.5, 0.5), loc='upper center', fontsize='small')
#self.disch_df.groupby(self.disch_df.index.month).mean().plot().legend(ncol=2, bbox_to_anchor=(.95, 0.55, 0.5, 0.5), loc='upper center', fontsize='small')
#plt.show()
