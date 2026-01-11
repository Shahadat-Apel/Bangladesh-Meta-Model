import FloodModule as FM 
import Cropmodule as CM
import SalinityModule as SM 
import outputModule as OM
import NetworkModule as NM
import os
import TimeIndexFunctions as TF
import datetime as dt


dataroot = os.getcwd()

networkmodule = NM.NetworkModuleClass(dataroot)
fmodule = FM.floodModuleClass()
cmodule = CM.cropModuleClass()
smodule = SM.SalinityModuleClass()
outPutmodule = OM.outputModuleClass()

beginTime = dt.date(1985,1,1)
endTime = dt.date(1985,5, 21)
startTimeIndex = TF.datetotimeindex(beginTime)
endTimeIndex = TF.datetotimeindex(endTime)

scenarioName = int(input("Enter Scenario Name : "))
#print(type(scenarioName) )
nmdata = networkmodule.initializeModuleforRun(scenarioName);
#print(nmodule.wlDataFrame.head(5))
networkmodule._wlDataFrame.to_csv(os.path.join(networkmodule._privatedatafolder,'Calibration\{}_wl.csv'.format(scenarioName)), sep=',',index=True) #"{}{}".format(s, y)
networkmodule._disch_df.to_csv(os.path.join(networkmodule._privatedatafolder,'Calibration\{}_Q.csv'.format(scenarioName)), sep=',',index=True)
networkmodule._tidalRange_df.to_csv(os.path.join(networkmodule._privatedatafolder,'Calibration\{}_TR.csv'.format(scenarioName)), sep=',',index=True)

fdata = fmodule.initializeModuleforRun()

damageFactor=cmodule.initializeModuleforRun()

outPutmodule.initializeModuleforRun()


    
for timeStepIndex in range(startTimeIndex, endTimeIndex):
        errorcode = networkmodule.dotimeStep(timeStepIndex)
        print(errorcode)
        if errorcode == 0:
            print(TF.timeindextodate(timeStepIndex),networkmodule.waterlevel['N330'])

networkmodule.postProssesing()
fmodule.postProssesing()
cmodule.postProssesing()
smodule.postProssesing()

databaseData=outPutmodule.postProssesing()

#print(networkResult[1])