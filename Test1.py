import pandas as pd
import numpy as np
area = pd.read_csv(r'data\S-Curve.csv')
#for x in area.iterrows():
    #temp = x.split(',')
    #print(x[1][0], ",",x[1][1] )
#print(area.head(5))
    up = pd.read_csv(r'data\upazila.csv')
upazila = []
upazila_emb = []
for x in up.iterrows():
    for y in range(2, 8):
        if x[1][8]==0:
            upazila.append(x[1][y])
        else:
            upazila_emb.append(x[1][8])
            break;
        
    #print(x[1][0], ",",x[1][2] )
upazila
upazila_emb
from matplotlib import pyplot as plt
wl = pd.read_csv(r'data\Grid_1.csv',sep=',', index_col=0, parse_dates=True)
fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize= (10,10))
wl.plot(ax=axes[0], drawstyle = "steps", label ="whole Time series")
wl.plot(ax=axes[1], drawstyle = "steps", label ="whole Time series")
for y in upazila:
    wl[wl>y].plot(ax=axes[0], drawstyle = "steps")
for t in upazila_emb:
    wl[wl>t].plot(ax=axes[1], drawstyle = "steps")
L=axes[0].legend()
L.get_texts()[0].set_text('VLL')
L.get_texts()[1].set_text('LL')
L.get_texts()[2].set_text('MLL')
L.get_texts()[3].set_text('HL')
L.get_texts()[4].set_text('VHL')
L.get_texts()[5].set_text('FFL')
L1=axes[1].legend()
L1.get_texts()[0].set_text('WL')
L1.get_texts()[1].set_text('Avobe Intervention')
plt.show()

