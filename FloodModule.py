import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

class floodModuleClass():
    def initializeModuleforRun(self):
        self.area = pd.read_csv(r'data\S-Curve.csv')
        self.wl = pd.read_csv(r'data\Grid_1.csv',sep=',', index_col=0, parse_dates=True)
        self.up = pd.read_csv(r'data\upazila.csv')
        self.upazila = []
        self.upazila_emb = []
        for x in self.up.iterrows():
            for y in range(2, 8):
                if x[1][8]==0:
                    self.upazila.append(x[1][y])
                else:
                    self.upazila_emb.append(x[1][8])
                    break
        self.upazila
        self.upazila_emb
        print("Flood module is initialized")

    def dotimeStep(self,currentTimStep):
        waterDepth = []
        Wl_temp= self.wl.iloc[currentTimStep]["WL"]
        vll= (Wl_temp>self.upazila[0]) & (Wl_temp < self.upazila[1])
        vllWD= vll-self.upazila[0]
        if vllWD <=0:
            vllWD=0
        waterDepth.append(vllWD)
        ll= (Wl_temp>self.upazila[1]) & (Wl_temp < self.upazila[2])
        llWD= ll-self.upazila[1]
        if llWD <=0:
            llWD=0
        waterDepth.append(llWD)   
        mll= (Wl_temp>self.upazila[2]) & (Wl_temp < self.upazila[3])
        mllWD= mll-self.upazila[2]
        if mllWD <=0:
            mllWD=0
        waterDepth.append(mllWD)
        mhl= (Wl_temp>self.upazila[2]) & (Wl_temp < self.upazila[3])
        mhlWD= mhl-self.upazila[2]
        if mhlWD <=0:
            mhlWD=0
        waterDepth.append(mhlWD)
        hl= (Wl_temp>self.upazila[2]) & (Wl_temp < self.upazila[3])
        hlWD= hl-self.upazila[2]
        if hlWD <=0:
            hlWD=0
        waterDepth.append(hlWD)
        
        Parea = []
        for elv in self.upazila:
            for area_temp in self.area.iterrows():
                if area_temp[1][1]>= elv:
                    Parea.append(area_temp[1][0])
                    break
        ActualFloodafectedArea=[]
        for landType in self.upazila:
            if landType <= Wl_temp:
                for i in range(0,len(self.area)): 
                    area_temp= self.area.iloc[i]
                    if area_temp[1]>= Wl_temp:
                         ActualFloodafectedArea.append(area_temp[0])
                     
            else:
                 ActualFloodafectedArea.append(0)
                 
        floodDuration=[10,7,5,4,3]
        
        return waterDepth, Parea, floodDuration
    
    
    def postProssesing(self):
      pass

    
    




