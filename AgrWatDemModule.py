# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 13:14:45 2019

@author: hegnauer
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime as dt
import TimeIndexFunctions as TF

class AgrWatDemModuleClass():
    def __init__(self,datarootfolder):
        self.privatedatafolder =  os.path.join(datarootfolder,"PrivateData")
        self.privatedatafolder =  os.path.join(self.privatedatafolder,"AgrWatDemModule")
        self.shareddatafolder = os.path.join(datarootfolder,"SharedData")

    def initializeModuleforRun(self):
        #calculate the cropping pattern per upzaila (544), landtype (5) and crop (15)
       
        #read input files per district, upazila and crop
        disFileName = os.path.join(self.privatedatafolder,'Tables\\District.csv')
        dis_df   = pd.read_csv(disFileName, sep=',', index_col=None)
        ndis= len(dis_df)
        upzFileName = os.path.join(self.privatedatafolder,'Tables\\Upazila.csv')
        upz_df   = pd.read_csv(upzFileName, sep=',', index_col=None)
        nupz= len(upz_df)
        crpFileName = os.path.join(self.privatedatafolder,'Tables\\Crop.csv')
        crp_df   = pd.read_csv(crpFileName, sep=',', index_col='Name')
        ncrop=len(crp_df)
        cropdata=crp_df.to_numpy(dtype='float64')
        
        #define 3D output matrix to stroe area per crop, landtype and uapzilla
        croppat=np.zeros((ncrop,5,nupz))
        #and a list for the THACODEs
        thacodes=list()
        
        #outputfile
        upzcropareafilname=os.path.join(self.privatedatafolder,'Output\\UpzCropArea.csv')
        upzcropareafil = open(upzcropareafilname,'wt')

        lupz=0
        for idis in range(ndis):
            dis = (dis_df.iloc[idis])
            #print(dis.District)
            #get summed upazila data for this district
            upzindis=upz_df[upz_df['DISTNAME']==dis.District]
            sumupz=upzindis.groupby(['DISTNAME'],as_index = False).sum()
            sumupz.reset_index()
            #create df with total area per landtype
            areaft=sumupz.iloc[0,2:7].to_numpy(dtype='float64')
            #create empty np matrix with crop area per landtype
            cropft=np.zeros((15,5))
            #fill in the Boro data summed over the Upazilas
            cropdis=dis[3:].to_numpy(dtype='float64')
            for landtype in range(0,5): 
                ft='Boro_F{}'.format(landtype)
                cropft[3,landtype]=float(sumupz.at[0,ft])
                if cropft[3,landtype] > areaft[landtype]: areaft[landtype] = cropft[3,landtype]  
            #set Boro in crop areas per district to zero
            cropdis[3]=0
            #calulate remaing areas per landtype
            remareaft=areaft-cropft[3]
            remareaft=np.where(remareaft < 0., 0.,remareaft)
            #create integer array with crop season type
            cropseas=cropdata[:,1].astype(int)
            #loop over croptype
            for croptype in (4,1,2,3):
                #allocate area for crop type 4 - annual crops
                crop01 = np.where(cropseas == croptype,1.,0.)
                croparea= cropdis * crop01
                croptot=np.sum(croparea)
                #loop over landtypes
                for lt in range (0,5):
                    fr_lt=min(1.,remareaft[lt]/croptot)
                    cropft[:,lt]=cropft[:,lt] + croparea*fr_lt

            #calculate for each crop fraction per landtype      
            croptot = np.sum(cropft,axis=1).reshape(15,1)
            #croptot = np.where(croptot == 0.,1.,croptot)
            fracft = cropft / np.where(areaft == 0., 1., areaft)            
            #print (cropft)
            
            #calculate the areas for each upazila per landtype and per crop 
            #loop over upazillas in district
            areaft=upzindis.iloc[:,4:9].to_numpy(dtype='float64')
  
            for iupz in range(len(upzindis)):
                upz=upzindis.iloc[iupz]
                thacodes.append(upz.THACODE)
                #for landtype in range(0,5): 
                #    ft='Boro_F{}'.format(landtype)
                #    croparea[3,landtype]=float(upz.at[ft])
                #    if croparea[3,landtype] > areaft[landtype]: areaft[landtype] = cropft[3,landtype]  
  
                croparea=fracft*areaft[iupz,:]
                croppat[:,:,lupz]=croparea
                lupz += 1
 
        #write output file with crop area per landtype and upazila        
        sline='thacode,crop,F0,F1,F2,F3,F4\n'
        upzcropareafil.write(sline)
        for iupz in range(nupz):
            for icrop in range(ncrop):
                sline='{},{}'.format(thacodes[iupz],icrop+1)
                for lt in range(5):
                    sline+=',{}'.format(croppat[icrop,lt,iupz])
                sline += '\n'
                upzcropareafil.write(sline)
        upzcropareafil.close()
        
        return thacodes,croppat
        
    def dotimeStep(self,currentTimeIndex):
        #calculate the PET in m3/decade per upazila, per landtype, per crop 
        pass
            
    def postProssesing(self):
        pass





def main():
    print("Self Testing from Water Agricultural Water Demand module")
    dataroot = os.getcwd()
    
    agrdemm = AgrWatDemModuleClass(dataroot)
    beginTime = dt.date(2001,1,1)
    endTime = dt.date(2001,5, 21)
    startTimeIndex = TF.datetotimeindex(beginTime)
    endTimeIndex = TF.datetotimeindex(endTime)
    #print(startTimeIndex, endTimeIndex)
    
    agrdemdata = agrdemm.initializeModuleforRun();
    for timeStepIndex in range(startTimeIndex, endTimeIndex):
        dateCurrentTimeIndex =TF.timeindextodate(timeStepIndex)

           
if __name__ == "__main__":
    main()  

