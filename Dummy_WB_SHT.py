# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 14:51:43 2020

@author: ASUS
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:35:28 2020

@author: Md. Shahadat Hossain, 
"""
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from calendar import monthrange
import TimeIndexFunctions as TF

class WaterBalanceClass():
    
    def __init__(self,datarootfolder):
        self._privatedatafolder =  os.path.join(datarootfolder,"PrivateData")
        self._privatedatafolder =  os.path.join(self._privatedatafolder,"WaterBalanceModule")
        self._shareddatafolder = os.path.join(datarootfolder,"SharedData")
    def decadeDay(self,year, month, day):
        if day<12:
            return 10
        elif day < 2:
            return 10
        else:
            return monthrange(year, month)[1]-20
    def gateOperation(self, month, day):
        if month<4 or (month<=4 and day< 2):
            return 0
        elif month>10 or (month >= 10 and day > 12):
            return 0
        else: return 1
    def pumpOperation(self, openParameter, closeParameter, decadaelist):
        if decadaelist < openParameter:
            return 0
        elif decadaelist> closeParameter:
            return 0
        else: return 1
    
    def initializeModuleforRun(self):
        self._waterBalanceParameter = os.path.join(self._privatedatafolder,'WBStaticParameters.csv')
        self._waterBalanceParameter_df   = pd.read_csv(self._waterBalanceParameter, sep=',', index_col=None)
        #print(self._waterBalanceParameter_df['Loss'][2])
        
        self._rf_evap_file = os.path.join(self._privatedatafolder,'BoundaryData_RF_EVAP.csv')
        self._rf_evap_df   = pd.read_csv(self._rf_evap_file, sep=',', index_col=0)
        self._rf_evap_df.index = pd.to_datetime(self._rf_evap_df.index, format="%d/%m/%Y")
        #Day count
        yearExtraction = list(self._rf_evap_df.index.year)
        monthExtraction = list(self._rf_evap_df.index.month)
        dayExtraction = list(self._rf_evap_df.index.day)
        self._rf_evap_df['Days'] = list(map(self.decadeDay, yearExtraction,monthExtraction,dayExtraction))
        
        #Constant
        self._rf_evap_df['Rootzone_store']= int(self._waterBalanceParameter_df['Rootzone_store'][2]) # replace by upazilla code
        self._rf_evap_df['Subsoil_store']= int(self._waterBalanceParameter_df['Sub-soil_store'][2]) # replace by upazilla code
        
        self._rf_evap_df['Subsoil_loss'] = self._rf_evap_df['Days'] * int( self._waterBalanceParameter_df['Loss'][2]) # replace by upazilla code
        #Init_timestep
        self._rf_evap_df['Fieldwl']= int(self._waterBalanceParameter_df['F3_wl'][2]) # replace by upazilla code

        self._rf_evap_df['Rootzonewl']= int(self._waterBalanceParameter_df['Rootzone_wl'][2]) # replace by upazilla code
        
        self._rf_evap_df['Subsoilwl']= int(self._waterBalanceParameter_df['Sub-soilwl'][2]) # replace by upazilla code
        
        #step 1
        self._rf_evap_df['Sub-soil_loss_s1']= self._rf_evap_df[['Subsoil_loss', 'Subsoilwl']].min(axis=1)
        self._rf_evap_df['Subsoilwl_s1']= self._rf_evap_df['Subsoilwl']-self._rf_evap_df['Sub-soil_loss_s1']
        #step 2
        self._rf_evap_df['P-ET_s2']= self._rf_evap_df['RF']-self._rf_evap_df['EVAP']
        #step 3
        self._rf_evap_df['Infil_s3']=pd.DataFrame({'s0':0, 's1': pd.DataFrame( {'s1': self._rf_evap_df['Fieldwl']+ self._rf_evap_df['P-ET_s2'], 's2':self._rf_evap_df['Rootzone_store']-self._rf_evap_df['Rootzonewl']}).min(axis=1)}).max(axis=1) 
        self._rf_evap_df['Actual_infil_s3']= np.where(self._rf_evap_df['Infil_s3']> int(self._waterBalanceParameter_df['Maxinfiltration_rate'][2])*self._rf_evap_df['Days'], int(self._waterBalanceParameter_df['Maxinfiltration_rate'][2])*self._rf_evap_df['Days'] ,self._rf_evap_df['Infil_s3']) # replace by upazilla code
        #step 4
        self._rf_evap_df['Fieldwl_s4']= self._rf_evap_df[['Fieldwl', 'P-ET_s2','Actual_infil_s3']].sum(axis=1)
        self._rf_evap_df['Rootzonewl_s4']= self._rf_evap_df[['Rootzonewl', 'Actual_infil_s3']].sum(axis=1)
        #Step 5
        self._rf_evap_df['Crop_deficit_s5']= np.where(self._rf_evap_df['Fieldwl_s4']>0,0, self._rf_evap_df['Fieldwl_s4'])
        self._rf_evap_df['Crop_avai_s5']= np.where(self._rf_evap_df['Rootzonewl_s4']<0,0, self._rf_evap_df['Rootzonewl_s4'])
        self._rf_evap_df['Crop_ava_s5']= pd.DataFrame({'s0':self._rf_evap_df['Crop_deficit_s5'].abs(), 's1':self._rf_evap_df['Crop_avai_s5']}).min(axis=1)
        self._rf_evap_df['Fieldwl_s5']= pd.DataFrame({'s0':self._rf_evap_df['Fieldwl_s4'], 's1':self._rf_evap_df[['Crop_ava_s5', 'Crop_deficit_s5']].sum(axis=1)}).max(axis=1)
        self._rf_evap_df['Rootzonewl_s5']= self._rf_evap_df['Rootzonewl_s4']-self._rf_evap_df['Crop_ava_s5']
        #step 6
        self._rf_evap_df['Percolation_s6']=pd.DataFrame({'s0':0, 's1': pd.DataFrame( {'s1': self._rf_evap_df['Rootzonewl_s5'], 's2':self._rf_evap_df['Subsoil_store']-self._rf_evap_df['Subsoilwl_s1']}).min(axis=1)}).max(axis=1) 
        self._rf_evap_df['Actual_perc_s6']= np.where(self._rf_evap_df['Percolation_s6']> int(self._waterBalanceParameter_df['Maxpercolation_rate'][2])*self._rf_evap_df['Days'], int(self._waterBalanceParameter_df['Maxpercolation_rate'][2])*self._rf_evap_df['Days'] ,self._rf_evap_df['Percolation_s6']) # replace by upazilla code
        # step 7
        self._rf_evap_df['Rootzonewl_s7']= self._rf_evap_df['Rootzonewl_s5']-self._rf_evap_df['Actual_perc_s6']
        self._rf_evap_df['Subsoilwl_s7']= self._rf_evap_df[['Subsoilwl_s1', 'Actual_perc_s6']].sum(axis=1)
        #Network step 8
        self._rf_evap_df['Gate_O_C']= list(map(self.gateOperation, monthExtraction,dayExtraction))
        self._rf_evap_df['Discharge_network'] = (self._rf_evap_df['Fieldwl_s5']-self._rf_evap_df['WL'])*self._rf_evap_df['Gate_O_C']
        self._rf_evap_df['Efficiency_network']=pd.DataFrame({'s0':(-1)* self._rf_evap_df['Days']*float(self._waterBalanceParameter_df['MaxDrainagerate'][2])/100, 's1': pd.DataFrame( {'s1': self._rf_evap_df['Discharge_network']* int(self._waterBalanceParameter_df['Drainage_eff'][2]) , 's2':self._rf_evap_df['Days']*int(self._waterBalanceParameter_df['MaxDrainagerate'][2])/100}).min(axis=1)}).max(axis=1) * self._rf_evap_df['Gate_O_C'] # replace by upazilla code
        self._rf_evap_df['Fieldwl_network'] = self._rf_evap_df['Fieldwl_s5']-self._rf_evap_df['Efficiency_network']
        #Pumped drainage step 9
        timeStep = list(map(TF.datetotimeindex, self._rf_evap_df.index))
        timeStepNumber = list(map(TF.timeindextodecade, timeStep))
        openParameter = int( self._waterBalanceParameter_df['Pump_on'][2])
        closeParameter = int (self._waterBalanceParameter_df['Pump_off'][2])
        #self._rf_evap_df['Pump_On_Off']= list(map(self.pumpOperation , openParameter, closeParameter, timeStepNumber))
        #print(type(openParameter))
        #print(closeParameter)
        
        #print(timeStepNumber)
        #print(self._rf_evap_df.head(40))

        firstTimesatep = TF.timeindextodecade(TF.datetotimeindex(self._rf_evap_df.index[0]))
        outPut_df = pd.DataFrame({'Timestep':[firstTimesatep]})
        outPut_df['Days'] = decadeDay(self._rf_evap_df.index[0])
        print(outPut_df)
        
        

 
       
        
        
        
        
     
    def dotimeStep(self):
        pass
    
    def postProssesing(self):
        pass
    
    
def main():
    print("Self Testing from WB module")
    dataroot = os.getcwd()
    nmodule = WaterBalanceClass(dataroot)
    nmodule.initializeModuleforRun()

    
if __name__ == "__main__":
    main()  