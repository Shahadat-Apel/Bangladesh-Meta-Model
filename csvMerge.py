# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 12:11:18 2019

@author: ASUS
"""
import psycopg2
import pandas as pd
import os
#from sqlalchemy import create_engine
#from openpyxl import Workbook
path = r'D:\Bangladesh_Metamodel\ModelScripts\PrivateData\NetworkModule\Calibration'
files_in_dir = [f for f in os.listdir(path) if f.endswith('.csv')]
frames = []
for filenames in files_in_dir: 
    df = pd.read_csv(os.path.join(path,filenames))
    df['case'] = filenames[0]
    if filenames[2:3] == "w":
        df['Parameter'] = 'Water Level (m)' 
    elif filenames[2:3] == "Q":
        df['Parameter'] = 'Discharge (m3/s)'
    elif filenames[2:3] == "T":
        df['Parameter'] = 'Tidal Range (m)' 
    else:
        pass
    frames.append(df)
    df =pd.DataFrame()
#    df.to_csv('out.csv', mode='a')
new_combined = pd.concat(frames,join='inner', ignore_index=True)
new_combined.insert(1, 'Month', new_combined['Date'].str.split('-', expand = True)[1])
new_combined.insert(2, 'Season', 1)
#new_combined.to_csv('results_bangladeshday.csv',index = False)
new_combined.to_excel('results_bangladeshday.xlsx',sheet_name='results_bangladeshday',index = False)



#####

#output = pd.read_csv("F:/JCPmetamodel/Git/MetamodelTest/ModelScripts/crop_losses.csv", sep=',', index_col=None)

#engine = create_engine('postgresql://postgres:db@adm@localhost:5432/metamodelDB')
#output.to_sql('crop_losses', engine, if_exists='replace', index=False, index_label=None, chunksize=None, dtype=None, method='multi')