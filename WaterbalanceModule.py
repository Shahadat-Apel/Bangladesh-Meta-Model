# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 13:14:45 2019

@author: Marnix van der Vat
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
import TimeIndexFunctions as TF

class WaterBalanceClass():
    """
    A class used to simulate the water balance at upazila level

    Inputs from framework
    ------
    networkmodule.waterlevel : pandas series with waterlevel of current timestep for each node
    networkmodule.discharge : pandas series with discharge of current timestep for each node
    agrdem.upz_df : pandas data frame with attributes of the upazilas    
    agrdem.thacodes(aggrdem.nupz) : list of upzazila codes
        with aggrdem.nupz - number of upzilas
    agrdem.croppat(agrdem.ncrop,agrdem.nltype,agrdem.nupz) : numpy array croppingpattern per crop, per land type and upzila ha
       with agrdem.nltype - number of landtypes
            agrdem.ncrop - number of crops
                       number of real crops is ncrop minus nexcrop
                       extra crops are used to describe other land use categories
            grdem.nexcrop - number of extra crop categories (5):- Forest
                                                                - Settlement
                                                                - Total agricultural Area 
                                                                - River
                                                                - Waterbodies
       for the extra crops areas are only for Total agricultural area divided over the landtypes
       for the other extra crops the area for the whole upzila is stored in croppat[icrop,0,iupz]
       with croppat[icrop,1:4,iupz] set to zero
      agrdem.cropwatdem(nltype+nexcrops,nupz) : numpy array crop water demand for considered timestep per landtype and upzila in mm/day
        crop water demand for real crops is calculated by summing the PET per land type and upazila over
        the different crops that have a Kc value > 0 for the actual decade and then dividing this by
        the area covered by these plants
        crop water demand for the other land use categories is calculated as PET
      agrdem.agrarea(agrdem.nltype,agrdem.nupz) : numpy array total crop area for the considered timestep per landtype and upazila

    Results to framework
    ----------
    qlat(agrdem.nupz) : numpy array with lateral discharges to (+) or from (-) the network in m3/s
                        flow from the upazila to te network is defined as positive
                        flow from the network to the upazila is defined as negative
    agrsupfract(agrdem.nltype,agrdem.upz) : numpy array with fraction of crop water demand that has been fulfilled  by the supply
    waterdepthonfield(agrdem.nltype,agrdem.upz) : numpy array with depth of the water above the field (0 means no water on the field)

    Methods
    -------
    initialzeModuleforRun(agrdem)
        reads the precipitation from file 
        reads the connection to the network nodes from file
        sets the initial values for the water balances
    dotimestep(currentTimeIndex,network,agrdem)
        simulates the water balance and calculates the exchange with the network per land type and upazila
        updates state variables of the water balance
    postprocessing()
        write the state variables so that they can be used as initial conditions
    """
    def __init__(self,datarootfolder):
        privatedatafolder =  os.path.join(datarootfolder,"PrivateData")
        self._privatedatafolder =  os.path.join(privatedatafolder,"WaterBalanceModule")
        self._shareddatafolder = os.path.join(datarootfolder,"SharedData")
        self.waterlevelsForNodes = None

    def initializeModuleforRun(self,startTime, endTime):
        #read the precipitation from file
        upzPrecipitationFileName = os.path.join(self._privatedatafolder,'Tables','Upz_P.csv')
        self._df_upzPrecipitation = pd.read_csv(upzPrecipitationFileName, sep=',',index_col=0)

        # read the evapotranspiration from file (not needed, if live link with AgrWatDemModule)
        upzPrecipitationFileName = os.path.join(self._privatedatafolder, 'Tables', 'Upz_ET.csv')
        self._df_upzEvapotranspiration = pd.read_csv(upzPrecipitationFileName, sep=',', index_col=0)

        #read the connection to the network nodes from file
        upztonodesFileName=os.path.join(self._privatedatafolder,'Tables','UPZtoNodes.csv')
        self._df_upztonodes = pd.read_csv(upztonodesFileName, sep=',',index_col=0)
        
        #initialize the values of the state variables from file
        initFileName=os.path.join(self._privatedatafolder,'Tables','init_wbupz.csv')
        self._df_statewl = pd.read_csv(initFileName, sep=',')
        # print(self._df_statewl.keys())

        #define temporary dataframes used for processing
        self._df_statewl_light = self._df_statewl[['THACODE', 'Total_area', 'project_area', 'pw', 'pw_wl', 'shr', 'shr_wl', 'F4', 'F4_wl', 'F3', 'F3_wl','F2', 'F2_wl','F1', 'F1_wl','F0', 'F0_wl','forest', 'Forest_wl','settl', 'Settl_wl', 'riv']]
        self._df_statewl_area = self._df_statewl_light.melt(['THACODE', 'Total_area', 'project_area', 'pw_wl', 'shr_wl', 'F4_wl', 'F3_wl', 'F2_wl', 'F1_wl', 'F0_wl', 'Forest_wl', 'Settl_wl'])
        self._df_statewl_wl = self._df_statewl_light.melt(['THACODE', 'Total_area', 'project_area', 'pw', 'shr', 'F4', 'F3', 'F2', 'F1', 'F0', 'forest', 'settl', 'riv'])

        self._df_statewl_area['index_col'] = self._df_statewl_area.index
        self._df_statewl_wl['index_col'] = self._df_statewl_wl.index

        #initialize calculation dataframe
        self._df_calculation = pd.merge(self._df_statewl_area[['index_col', 'THACODE', 'Total_area','variable', 'value']], self._df_statewl_wl[['index_col', 'value']], on='index_col', sort=False)
        self._df_calculation = self._df_calculation.rename(columns={"variable": "landtype", "value_x": "lt_area", "value_y": "field_wl"})
        self._df_calculation["lt_area"] = self._df_calculation["lt_area"] * self._df_calculation["Total_area"]
        self._df_calculation["lt_area"] = self._df_calculation["lt_area"].astype({'lt_area':'int32'})
        self._df_calculation = self._df_calculation.drop(columns=['Total_area'])
        list_of_constants = ['THACODE', 'Rootzone_wl', 'Sub-soilwl', 'Rootzone_store', 'Sub-soil_store', 'Loss', 'Maxinfiltration_rate', 'Maxpercolation_rate']
        self._df_calculation = pd.merge(self._df_calculation, self._df_statewl[list_of_constants], on='THACODE')

        # is_Upazila = self._df_calculation['THACODE']==302674
        # print(self._df_calculation[is_Upazila])
        # print(self._df_calculation.keys())
        self._timesteps = endTime - startTime
        self._endTime = endTime
        self.calculatedresult = np.zeros((self._timesteps,4707,4))  ## public variable is available outside of module
        
    def dotimeStep(self,currentTimeIndex):
        print(currentTimeIndex)
        print(self.waterlevelsForNodes)
        length_of_decade = TF.lengthofdecade(currentTimeIndex)

        # Step 1: release water from substratum
        self._df_calculation['Subsoil_loss'] = self._df_calculation['Loss'] * length_of_decade
        self._df_calculation['Subsoil_loss_actual'] = np.min(self._df_calculation[['Subsoil_loss', 'Sub-soilwl']], axis=1)      # in case of finding minimum of columns
        self._df_calculation['Sub-soilwl'] = self._df_calculation['Sub-soilwl'] - self._df_calculation['Subsoil_loss_actual']

        # Step 2: derive difference between supply and demand
        # First, parse supply
        self._df_upzPrec= self._df_upzPrecipitation.loc[[currentTimeIndex]].T      # transpose
        self._df_upzPrec.index = self._df_upzPrec.index.map(int)    # change of datatype required because, otherwise merge is not possible
        self._df_calculation = pd.merge (self._df_calculation, self._df_upzPrec, left_on='THACODE', right_index= True)

        # Second, parse demand (should become an active link with AgrWatDemModule.py)
        self._df_upzET = self._df_upzEvapotranspiration.loc[[currentTimeIndex]]
        # print(self._df_upzET.keys())
        self._df_calculation = pd.merge (self._df_calculation, self._df_upzET, left_on='THACODE', right_on='upz')

        # Third, calculate diff
        self._df_calculation['PminET'] = self._df_calculation[currentTimeIndex] - self._df_calculation['PET_F0']

        # Step 3: calculate actual infiltration
        self._df_calculation['Infil'] = np.maximum(0,np.minimum((self._df_calculation['field_wl'] + self._df_calculation['PminET']),(self._df_calculation['Rootzone_store'] - self._df_calculation['Rootzone_wl'])))
        self._df_calculation['maxInfil'] = self._df_calculation['Maxinfiltration_rate'] * length_of_decade
        self._df_calculation['actInfil'] = np.min(self._df_calculation[['Infil', 'maxInfil']], axis=1)

        # Step 4: update field and rootzone waterlevel by infiltration
        self._df_calculation['field_wl'] = self._df_calculation['field_wl'] + self._df_calculation['PminET'] - self._df_calculation['actInfil']
        self._df_calculation['Rootzone_wl'] = self._df_calculation['Rootzone_wl'] + self._df_calculation['actInfil']

        # Step 5: if required release water from rootzone for crop water demand and update field and rootzone waterlevel through water supply crops
        self._df_calculation['crop_deficit'] = np.minimum(0, self._df_calculation['field_wl'])
        self._df_calculation['pot_crop_avail'] = np.maximum(0, self._df_calculation['Rootzone_wl'])
        self._df_calculation['act_crop_avail'] = np.minimum(np.abs(self._df_calculation['crop_deficit']), self._df_calculation['pot_crop_avail'])
        self._df_calculation['field_wl'] = np.maximum(self._df_calculation['field_wl'], (self._df_calculation['Rootzone_wl'] + self._df_calculation['crop_deficit']))
        self._df_calculation['Rootzone_wl'] = self._df_calculation['Rootzone_wl'] - self._df_calculation['act_crop_avail']

        # Step 6: calculate actual percolation
        self._df_calculation['Percol'] = np.maximum(0, np.minimum(self._df_calculation['Rootzone_wl'], (self._df_calculation['Sub-soil_store'] - self._df_calculation['Sub-soilwl'])))
        self._df_calculation['maxPercol'] = self._df_calculation['Maxpercolation_rate'] * length_of_decade
        self._df_calculation['actPercol'] = np.min(self._df_calculation[['Percol', 'maxPercol']], axis=1)

        # Step 7: update rootzone and subsoil waterlevel by percolation
        self._df_calculation['Rootzone_wl'] = self._df_calculation['Rootzone_wl'] - self._df_calculation['actPercol']
        self._df_calculation['Sub-soil_wl'] = self._df_calculation['Sub-soilwl'] + self._df_calculation['actPercol']

        # # Test and check for one upazila
        is_Upazila = self._df_calculation['THACODE'] == 100409          # 302674
        # print(self._df_calculation[is_Upazila][['landtype', 'field_wl', 'Rootzone_wl', 'Sub-soilwl']])
        self._df_output = self._df_calculation[is_Upazila][['landtype', 'field_wl', 'Rootzone_wl', 'Sub-soilwl']].T
        # print(self._df_calculation[is_Upazila][['index_col', 'Sub-soilwl', 'Subsoil_loss_actual', 'Subsoil_loss', currentTimeIndex, 'PET_F0', 'PminET', 'actInfil', 'act_crop_avail', 'actPercol']])

        # Clean up dataframe for next step
        list_of_constants = ['index_col','THACODE', 'landtype', 'lt_area', 'field_wl','Rootzone_wl', 'Sub-soilwl', 'Rootzone_store', 'Sub-soil_store', 'Loss', 'Maxinfiltration_rate', 'Maxpercolation_rate']
        self._df_calculation = self._df_calculation[list_of_constants]

        # Add dataframe to numpy array for postProcessing
        self.calculatedresult[self._endTime - currentTimeIndex-1,:,:] = self._df_calculation[['index_col', 'field_wl', 'Rootzone_wl', 'Sub-soilwl']].to_numpy()  ## public variable is available outside of module
        return 0
            
    def postProcessing(self):
        self.waterbalanceresult_trans = self.calculatedresult.transpose((2, 0, 1))
        print(self.waterbalanceresult_trans)

def main():
    print("Self Testing Water Balance module")
    dataroot = os.getcwd()
    
    dummywaterbalance = WaterBalanceClass(dataroot)
    beginTime = dt.date(2001,1,1)
    endTime = dt.date(2001,5,21)
    startTimeIndex = TF.datetotimeindex(beginTime)
    endTimeIndex = TF.datetotimeindex(endTime)
    print(startTimeIndex, endTimeIndex)
    # global test
    
    code = dummywaterbalance.initializeModuleforRun(startTimeIndex, endTimeIndex);
    for timeStepIndex in range(startTimeIndex, endTimeIndex):
        dateCurrentTimeIndex =TF.timeindextodate(timeStepIndex)
        test = dummywaterbalance.dotimeStep(timeStepIndex)
        waterbalanceresult = dummywaterbalance.calculatedresult

    dummywaterbalance.postProcessing()

           
if __name__ == "__main__":
    main()  

