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
import datetime as dt
import TimeIndexFunctions as TF
from datetime import timedelta

class WaterBalanceClass():
    
    def __init__(self,datarootfolder):
        self._privatedatafolder =  os.path.join(datarootfolder,"PrivateData")
        self._privatedatafolder =  os.path.join(self._privatedatafolder,"WaterBalanceModule")
        self._shareddatafolder = os.path.join(datarootfolder,"SharedData")
    def decadeDay(self,date):
        if date.day<12:
            return 10
        elif date.day < 2:
            return 10
        else:
            return monthrange(date.year, date.month)[1]-20
    def gateOperation(self,date):
        if date.month<4 or (date.month<=4 and date.day< 2):
            return 0
        elif date.month>10 or (date.month >= 10 and date.day > 12):
            return 0
        else: return 1
    def pumpOperation(self, openParameter, closeParameter, decadeDay):
        if  decadeDay < openParameter:
            return 0
        elif  decadeDay > closeParameter:
            return 0
        else: return 1
    def irrigationpumpOperation(self, timeStep,openParameter, closeParameter, SW_irrigation):
        if  timeStep < openParameter:
            return 0
        elif  timeStep > closeParameter:
            return 0
        else: return SW_irrigation/100
    
    def initializeModuleforRun(self, startTimeIndex):
        
        self._waterBalanceParameter = os.path.join(self._privatedatafolder,'WBStaticParameters.csv')
        self._waterBalanceParameter_df   = pd.read_csv(self._waterBalanceParameter, sep=',', index_col=None)
        #print(self._waterBalanceParameter_df['Loss'][1])
        
        self._rf_evap_file = os.path.join(self._privatedatafolder,'BoundaryData_RF_EVAP.csv')
        self._rf_evap_df   = pd.read_csv(self._rf_evap_file, sep=',', index_col=0)
        self._rf_evap_df.index = pd.to_datetime(self._rf_evap_df.index, format="%d/%m/%Y")
        
        indexTime = startTimeIndex
        date = pd.date_range( TF.timeindextodate(indexTime), TF.timeindextodate(indexTime),freq='D')[0]
        loc_step = self._rf_evap_df.index.get_loc(date)
        #print(loc_step)
        #print('-------------------------------------')

        firstTimesatep = TF.timeindextodecade(TF.datetotimeindex(self._rf_evap_df.index[loc_step]))
        self._outPut_df = pd.DataFrame({'Timestep':[firstTimesatep]}, index= [self._rf_evap_df.index[loc_step]])
        self._outPut_df['Days'] = self.decadeDay(self._rf_evap_df.index[loc_step])
        
        #Constant
        self._outPut_df['Rootzone_store']= int(self._waterBalanceParameter_df['Rootzone_store'][1]) # replace by upazilla code
        self._outPut_df['Subsoil_store']= int(self._waterBalanceParameter_df['Sub-soil_store'][1]) # replace by upazilla code
        self._outPut_df['Subsoil_loss'] = self._outPut_df['Days'] * int( self._waterBalanceParameter_df['Loss'][1]) # replace by upazilla code
        #Init_timestep
        self._outPut_df['Fieldwl']= int(self._waterBalanceParameter_df['F3_wl'][1]) # replace by upazilla code
        self._outPut_df['Rootzonewl']= int(self._waterBalanceParameter_df['Rootzone_wl'][1]) # replace by upazilla code
        self._outPut_df['Subsoilwl']= int(self._waterBalanceParameter_df['Sub-soilwl'][1]) # replace by upazilla code
        #step 1
        self._outPut_df['Sub-soil_loss_s1']= self._outPut_df[['Subsoil_loss', 'Subsoilwl']].min(axis=1)
        self._outPut_df['Subsoilwl_s1']= self._outPut_df['Subsoilwl']-self._outPut_df['Sub-soil_loss_s1']
        #step 2
        self._outPut_df['P-ET_s2']= self._rf_evap_df['RF'][loc_step]-self._rf_evap_df['EVAP'][loc_step]
        #step 3
        self._outPut_df['Infil_s3']=pd.DataFrame({'s0':0, 's1': pd.DataFrame( {'s1': self._outPut_df['Fieldwl']+ self._outPut_df['P-ET_s2'], 's2':self._outPut_df['Rootzone_store']-self._outPut_df['Rootzonewl']}).min(axis=1)}).max(axis=1) 
        self._outPut_df['Actual_infil_s3']= np.where(self._outPut_df['Infil_s3']> int(self._waterBalanceParameter_df['Maxinfiltration_rate'][1])*self._outPut_df['Days'], int(self._waterBalanceParameter_df['Maxinfiltration_rate'][1])*self._outPut_df['Days'] ,self._outPut_df['Infil_s3']) # replace by upazilla code
        #step 4
        self._outPut_df['Fieldwl_s4']= self._outPut_df[['Fieldwl', 'P-ET_s2']].sum(axis=1)- self._outPut_df['Actual_infil_s3']
        self._outPut_df['Rootzonewl_s4']= self._outPut_df[['Rootzonewl', 'Actual_infil_s3']].sum(axis=1)
        #Step 5
        self._outPut_df['Crop_deficit_s5']= np.where(self._outPut_df['Fieldwl_s4']>0,0, self._outPut_df['Fieldwl_s4'])
        self._outPut_df['Crop_avai_s5']= np.where(self._outPut_df['Rootzonewl_s4']<0,0, self._outPut_df['Rootzonewl_s4'])
        self._outPut_df['Crop_ava_s5']= pd.DataFrame({'s0':self._outPut_df['Crop_deficit_s5'].abs(), 's1':self._outPut_df['Crop_avai_s5']}).min(axis=1)
        self._outPut_df['Fieldwl_s5']= pd.DataFrame({'s0':self._outPut_df['Fieldwl_s4'], 's1':self._outPut_df[['Crop_ava_s5', 'Crop_deficit_s5']].sum(axis=1)}).max(axis=1)
        self._outPut_df['Rootzonewl_s5']= self._outPut_df['Rootzonewl_s4']-self._outPut_df['Crop_ava_s5']
        #step 6
        self._outPut_df['Percolation_s6']=pd.DataFrame({'s0':0, 's1': pd.DataFrame( {'s1': self._outPut_df['Rootzonewl_s5'], 's2':self._outPut_df['Subsoil_store']-self._outPut_df['Subsoilwl_s1']}).min(axis=1)}).max(axis=1) 
        self._outPut_df['Actual_perc_s6']= np.where(self._outPut_df['Percolation_s6']> int(self._waterBalanceParameter_df['Maxpercolation_rate'][1])*self._outPut_df['Days'], int(self._waterBalanceParameter_df['Maxpercolation_rate'][1])*self._outPut_df['Days'] ,self._outPut_df['Percolation_s6']) # replace by upazilla code
        # step 7
        self._outPut_df['Rootzonewl_s7']= self._outPut_df['Rootzonewl_s5']-self._outPut_df['Actual_perc_s6']
        self._outPut_df['Subsoilwl_s7']= self._outPut_df[['Subsoilwl_s1', 'Actual_perc_s6']].sum(axis=1)
        #Network step 8
        self._outPut_df['Gate_O_C']= self.gateOperation(self._rf_evap_df.index[loc_step])
        self._outPut_df['Discharge_network'] = (self._outPut_df['Fieldwl_s5']-self._rf_evap_df['WL'][loc_step])*self._outPut_df['Gate_O_C'] # water level is variable here
        self._outPut_df['Efficiency_network']=pd.DataFrame({'s0':(-1)* self._outPut_df['Days']*float(self._waterBalanceParameter_df['MaxDrainagerate'][1]), 's1': pd.DataFrame( {'s1': self._outPut_df['Discharge_network']* float(self._waterBalanceParameter_df['Drainage_eff'][1])/100 , 's2':self._outPut_df['Days']*float(self._waterBalanceParameter_df['MaxDrainagerate'][1])}).min(axis=1)}).max(axis=1) * self._outPut_df['Gate_O_C'] # replace by upazilla code
        self._outPut_df['Fieldwl_network'] = self._outPut_df['Fieldwl_s5']-self._outPut_df['Efficiency_network']
        #Pumped drainage step 9
        openParameter = int( self._waterBalanceParameter_df['Pump_on'][1])
        closeParameter = int (self._waterBalanceParameter_df['Pump_off'][1])
        self._outPut_df['Pump_On_Off_PD']= self.pumpOperation ( openParameter, closeParameter, self._outPut_df['Timestep'][0])
        self._outPut_df['Head_pos_neg_PD']= max(0,self._outPut_df['Fieldwl_network'][0] - self._rf_evap_df['WL'][loc_step]) # water make variable
        self._outPut_df['Discharge_PD']= self._outPut_df['Pump_On_Off_PD']* float(self._waterBalanceParameter_df['MaxDrainagerate'][1])* self._outPut_df['Days']
        self._outPut_df['Act_disch_PD']= max(0, self._outPut_df[['Head_pos_neg_PD','Discharge_PD']].min(axis=1)[0])
        self._outPut_df['Fieldwl_PD'] = self._outPut_df['Fieldwl_network']- self._outPut_df['Act_disch_PD']
        # SW Irrigation pump
        self._outPut_df['Irripump_On_Off_SW_IP'] = self.irrigationpumpOperation( self._outPut_df['Timestep'][0] , int( self._waterBalanceParameter_df['Irripump_on'][1]), int( self._waterBalanceParameter_df['Irripump_off'][1]), float( self._waterBalanceParameter_df['SW_irrigation'][1]))
        self._outPut_df['Head_neg_On_Off_SW_IP'] = max(0, self._rf_evap_df['WL'][loc_step]- self._outPut_df['Fieldwl_PD'][0]) # replace by timePu
        self._outPut_df['Discharge_SW_IP'] = min(abs(self._outPut_df['Fieldwl_PD'][0]),self._outPut_df['Irripump_On_Off_SW_IP'][0]*self._outPut_df['Days'][0]*int( self._waterBalanceParameter_df['MaxSWIrripump'][1]) )
        self._outPut_df['Act_disch_SW_IP'] = max(0, self._outPut_df[['Head_neg_On_Off_SW_IP', 'Discharge_SW_IP']].min(axis=1)[0])
        self._outPut_df['Fieldwl_SW_IP'] =  self._outPut_df['Fieldwl_PD'][0] + self._outPut_df['Act_disch_SW_IP'][0]*float( self._waterBalanceParameter_df['SW_irri_eff'][1])/100
        self._outPut_df['Rootzone_wl_SW_IP'] = self._outPut_df['Rootzonewl_s7'][0]+self._outPut_df['Act_disch_SW_IP'][0]*(1-float( self._waterBalanceParameter_df['SW_irri_eff'][1])/100)
        #GW irrigation
        self._outPut_df['Crop_deficit_GWI'] = min(0,self._outPut_df['Fieldwl_SW_IP'][0])
        self._outPut_df['Irrigationcap_GWI'] = max(0, min(self._outPut_df['Subsoilwl_s7'][0],float( self._waterBalanceParameter_df['MaxGWIrri'][1])*self._outPut_df['Days'][0] ))
        self._outPut_df['Act_Irri_cap_GWI'] = min(abs(self._outPut_df['Crop_deficit_GWI'][0]),self._outPut_df['Irrigationcap_GWI'][0])*float( self._waterBalanceParameter_df['GW_irrigation'][1])/100
        #Final_output
        self._outPut_df['Fieldwl_Final'] = max(self._outPut_df['Fieldwl_SW_IP'][0], self._outPut_df['Crop_deficit_GWI'][0]+self._outPut_df['Act_Irri_cap_GWI'][0]* float( self._waterBalanceParameter_df['GW_irri_eff'][1])/100)
        self._outPut_df['Rootzone_wl_Final'] = self._outPut_df['Rootzone_wl_SW_IP'][0]+ self._outPut_df['Act_Irri_cap_GWI'][0]* (1-float( self._waterBalanceParameter_df['GW_irri_eff'][1])/100)
        self._outPut_df['Subsoilwl_Final'] = self._outPut_df['Subsoilwl_s7'][0]-self._outPut_df['Act_Irri_cap_GWI'][0]

        
        #Network step 8
        #print(self._outPut_df)
        #print(len(self._outPut_df.columns))
        #print(float( self._waterBalanceParameter_df['SW_irrigation'][1]) )
        #self._outPut_df.to_csv("me.csv", sep=',')
       
        
     
    def dotimeStep(self, startTimeIndex, endTimeIndex):
        maxNoTimeStep= endTimeIndex-startTimeIndex
        for i in range(1, maxNoTimeStep+1): #self._rf_evap_df.shape[0]-1000
            indexTime = startTimeIndex+i
            date = pd.date_range( TF.timeindextodate(indexTime), TF.timeindextodate(indexTime),freq='D')[0]
            loc_step = self._rf_evap_df.index.get_loc(date)
            #print(loc_step)
            row = []
            row.append(TF.timeindextodecade(TF.datetotimeindex(self._rf_evap_df.index[loc_step]))) # 0 Timestep
            row.append(self.decadeDay(self._rf_evap_df.index[loc_step])) # 1 Days
            #Constant
            row.append(float(self._waterBalanceParameter_df['Rootzone_store'][1])) # 2 Rootzone_store 
            row.append(float(self._waterBalanceParameter_df['Sub-soil_store'][1])) # 3 Subsoil_store
            row.append(row[1]* float( self._waterBalanceParameter_df['Loss'][1])) # 4 Subsoil_loss
            #Init_timestep
            row.append(self._outPut_df['Fieldwl_Final'][i-1]) # 5 Fieldwl
            row.append(self._outPut_df['Rootzone_wl_Final'][i-1]) #6 Rootzonewl
            row.append(self._outPut_df['Subsoilwl_Final'][i-1]) #7 Subsoilwl
            #step 1
            row.append( min(row[4], row[7])) #8 Sub-soil_loss_s1
            row.append( row[7]- row[8]) #9 Subsoilwl_s1 
            #step 2
            row.append( self._rf_evap_df['RF'][loc_step]-self._rf_evap_df['EVAP'][loc_step]) #10 P-ET_s2
            #step 3
            row.append( max(0, min(row[5]+ row[10],row[2]-row[6])))  #11 Infil_s3
            row.append( np.where(row[11]> float(self._waterBalanceParameter_df['Maxinfiltration_rate'][1])*row[1], float(self._waterBalanceParameter_df['Maxinfiltration_rate'][1])*row[1] ,row[11])) # 12 Actual_infil_s3 
            #step 4
            row.append(row[5]+row[10]-row[12]) #13 Fieldwl_s4
            row.append(row[6]+row[12]) # 14 Rootzonewl_s4
            #Step 5
            row.append(np.where(row[13]>0,0, row[13])) # 15 Crop_deficit_s5
            row.append(np.where(row[14]<0,0, row[14])) #16 Crop_avai_s5
            row.append(min(abs(row[15]), row[16])) #17 Crop_ava_s5
            row.append(max(row[13], row[15]+row[17])) #18 Fieldwl_s5
            row.append(row[14]-row[17])  # 19 Rootzonewl_s5
            #step 6
            row.append(max(0,min(row[19], row[3]-row[9])))  #20 Percolation_s6
            row.append(np.where(row[20]> float(self._waterBalanceParameter_df['Maxpercolation_rate'][1])*row[1], float(self._waterBalanceParameter_df['Maxpercolation_rate'][1])*row[1] ,row[20])) # 21 Actual_perc_s6 -----replace by upazilla code
            # step 7
            row.append( row[19]-row[21]) # 22 Rootzonewl_s7
            row.append(row[9]+ row[21])  # 23  Subsoilwl_s7 
            #self._outPut_df['Subsoilwl_s7']= self._outPut_df[['Subsoilwl_s1', 'Actual_perc_s6']].sum(axis=1)
            #Network step 8
            #print(self._rf_evap_df.index[i])
            row.append(self.gateOperation(self._rf_evap_df.index[loc_step])) # 24 Gate_O_C'
            row.append((row[18]-self._rf_evap_df['WL'][loc_step])*row[24]) # 25 Discharge_network ---- water level is variable here
            row.append(max(-1*row[1]* float(self._waterBalanceParameter_df['MaxDrainagerate'][1]), min(row[25]* int(self._waterBalanceParameter_df['Drainage_eff'][1])/100 , row[1]*float(self._waterBalanceParameter_df['MaxDrainagerate'][1])))* row[24])  # 26 Efficiency_network---- replace by upazilla code
            row.append( row[18]-row[26]) # 27 Fieldwl_network
            #Pumped drainage step 9
            openParameter = int( self._waterBalanceParameter_df['Pump_on'][1])
            closeParameter = int (self._waterBalanceParameter_df['Pump_off'][1])
            row.append(self.pumpOperation ( openParameter, closeParameter, row[0]) )# 28 Pump_On_Off_PD
            row.append(max(0,row[27] - self._rf_evap_df['WL'][loc_step])) # 29 Head_pos_neg_PD ------water make variable
            row.append(row[28]* float(self._waterBalanceParameter_df['MaxDrainagerate'][1])*row[1]) # 30 Discharge_PD
            row.append(max(0, min(row[29],row[30]))) #31 Act_disch_PD
            row.append(row[27]-row[31]) #32 Fieldwl_PD
            # SW Irrigation pump
            row.append(self.irrigationpumpOperation( row[0] , int( self._waterBalanceParameter_df['Irripump_on'][1]), int( self._waterBalanceParameter_df['Irripump_off'][1]), float( self._waterBalanceParameter_df['SW_irrigation'][1]))) # 33 Irripump_On_Off_SW_IP
            row.append( max(0, self._rf_evap_df['WL'][loc_step]- row[32])) # 34 Head_neg_On_Off_SW_IP---- replace by timePu
            row.append(min(abs(row[32]),row[33]*row[1]*float( self._waterBalanceParameter_df['MaxSWIrripump'][1]))) #35 Discharge_SW_IP MaxSWIrripump
            row.append(max(0, min(row[34], row[35])))  # 36 Act_disch_SW_IP
            row.append(row[32] + row[36]*float( self._waterBalanceParameter_df['SW_irri_eff'][1])/100) #37 Fieldwl_SW_IP
            row.append(row[22]+row[36]*(1-float( self._waterBalanceParameter_df['SW_irri_eff'][1])/100)) #38 Rootzone_wl_SW_IP 
            #GW irrigation
            row.append( min(0,row[37])) # 39 Crop_deficit_GWI
            row.append(max(0, min(row[23],float( self._waterBalanceParameter_df['MaxGWIrri'][1])*row[1]))) # 40 Irrigationcap_GWI Irrigationcap_GWI
            #self._outPut_df['Irrigationcap_GWI'] = max(0, min(self._outPut_df['Subsoilwl_s7'][0],float( self._waterBalanceParameter_df['MaxGWIrri'][1])*self._outPut_df['Days'][0] ))
            row.append(min(abs(row[39]),row[40])*float( self._waterBalanceParameter_df['GW_irrigation'][1])/100) # 41 Act_Irri_cap_GWI
            #Final_output
            row.append( max(row[37], row[39]+row[41]* float( self._waterBalanceParameter_df['GW_irri_eff'][1])/100)) # 42 Fieldwl_Final
            row.append(row[38]+ row[41]* (1-float( self._waterBalanceParameter_df['GW_irri_eff'][1])/100)) # 43 Rootzone_wl_Final
            row.append(row[23]-row[41]) # 44 Subsoilwl_Final
            self._outPut_df.loc[date] = row
        self._outPut_df.to_csv('output.csv', sep=',')
        
            
            
    def postProssesing(self):
        pass
    
    
def main():
    print("Self Testing from WB module")
    beginTime = dt.date(2000,1,1)
    endTime = dt.date(2001,5, 21)
    startTimeIndex = TF.datetotimeindex(beginTime)
    endTimeIndex = TF.datetotimeindex(endTime)
    
    dataroot = os.getcwd()
    nmodule = WaterBalanceClass(dataroot)
    nmodule.initializeModuleforRun(startTimeIndex)
    nmodule.dotimeStep(startTimeIndex, endTimeIndex)

    
if __name__ == "__main__":
    main()  