import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

class cropModuleClass():
    def initializeModuleforRun(self):
        self.damageFactor = pd.read_csv(r'data\Rice_Damage_Factor.csv', index_col=0)
#        print(self.damageFactor)
        self.optimalYieldRate = 4
        self.area = 1
    def dotimeStep(self,currentTimeStep, fmResult):
        vllarea = fmResult[1][0]
        llarea = fmResult[1][1]-fmResult[1][0]
        mllarea = fmResult[1][2]-fmResult[1][1]
        mhlarea = fmResult[1][3]-fmResult[1][2]
        hlarea = fmResult[1][4]-fmResult[1][3]
        
        print(vllarea,llarea, mllarea, mhlarea, hlarea )
        waterDepthList= fmResult[0]
        wdDurationList= fmResult[2]
        floodedArea = fmResult[1]
        actualDamageList = []

        for wd in waterDepthList: 
            if wd<=0.25:
                for wdu in wdDurationList:
                    if wdu <= 2:
                        damageclass=1
                    elif wdu >2 & wdu<=6:
                        damageclass = 5
                    elif wdu >6:
                        damageclass = 9
            elif wd<=0.5:
                for wdu in wdDurationList:
                    if wdu <= 2:
                        damageclass=2
                    elif wdu >2 & wdu<=6:
                       damageclass = 6
                    elif wdu >6:
                        damageclass = 10
            elif wd<=0.75:
                for wdu in wdDurationList:
                    if wdu <= 2:
                        damageclass=3
                    elif wdu >2 & wdu<=6:
                       damageclass = 7
                    elif wdu >6:
                        damageclass = 11
            elif wd>0.75:
                for wdu in wdDurationList:
                    if wdu <= 2:
                        damageclass=4
                    elif wdu >2 & wdu<=6:
                       damageclass = 8
                    elif wdu >6:
                        damageclass = 12
            damage = self.damageFactor.iloc[damageclass-1][2]
            actualDamageList.append(damage)
        actualDamageMH = self.optimalYieldRate*self.area*mhlarea/100*actualDamageList[3]
        actualDamageH = self.optimalYieldRate*self.area*hlarea/100*actualDamageList[4]
        ActualProductionMH = self.optimalYieldRate*self.area*mhlarea/100 - actualDamageMH
        ActualProductionH = self.optimalYieldRate*self.area*hlarea/100 - actualDamageH
        totalActualProduction = ActualProductionMH+ActualProductionH
        totalLoss=actualDamageMH+actualDamageH
        print(totalLoss,totalActualProduction)
#            print(self.damageFactor.iloc[damageclass-1][2], wd, wdu)
#print("Damage due to flood (ton):", round(area* yeild * 0.6,0))
        
        
#        if fmResult[0][3] > 0.5:
#            print(currentTimeStep, " Medium high land is goint to be crop damaged")
#        if fmResult[0][4] > 0.5:
#            print(currentTimeStep, " high land is goint to be crop damaged")
        
    def postProssesing(self):
        pass
    
    




