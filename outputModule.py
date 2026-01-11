import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import datetime

class outputModuleClass():
    def initializeModuleforRun(self):
        self.colomnList = ["model_date", "upz_code", "crop_type_id",	"area_affected_ha",	"loss_type_id",	"loss_mt",	"senario_strategy_id"]
        self.dfCroplossOutput = pd.DataFrame(columns=self.colomnList)
        self.dfCroplossOutput.index.name = 'id'
        #print(self.dfCroplossOutput.head())
    
    def dotimeStep(self,currentTimStep):
        date = datetime.datetime(2010, 5, 17).strftime("%Y-%m-%d")
        upz_code= 100409
        crop_type_id =3
        area_affected_ha= 3.05
        loss_type_id= 3
        loss_mt = 42.00
        senario_strategy_id= 3
        colomnValue= [date, upz_code, crop_type_id, area_affected_ha, loss_type_id, loss_mt, senario_strategy_id]
        dictionary = dict(zip(self.colomnList ,colomnValue))
        
        self.dfCroplossOutput= self.dfCroplossOutput.append(dictionary, ignore_index=True)  
        
        #print(self.dfCroplossOutput.loc[0])
        
        
        
        
        
    
    def postProssesing(self):
        self.dfCroplossOutput.index.name = 'id'
        self.dfCroplossOutput.index += 1
        
        self.dfCroplossOutput.to_csv("crop_losses.csv", sep=',',index=True)
        return self.dfCroplossOutput
        

