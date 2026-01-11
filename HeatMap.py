# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 22:53:12 2019

@author: ASUS
"""

import numpy as np
#import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
# sphinx_gallery_thumbnail_number = 2
dataFrame  = pd.read_csv(r"C:\Users\ASUS\Desktop\Data.csv", sep=',', index_col=None)
#print(dataFrame.head())
stationData = dataFrame['station'].values
monthData =dataFrame.columns.values[1:]
dataAvailability = dataFrame[monthData].loc[:].values
dataAvailability = dataAvailability.astype(int)



fig, ax = plt.subplots()
im = ax.imshow(dataAvailability)

# We want to show all ticks...
ax.set_xticks(np.arange(len(monthData)))
ax.set_yticks(np.arange(len(stationData)))
# ... and label them with the respective list entries
ax.set_xticklabels(monthData)
ax.set_yticklabels(stationData)

# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation='vertical', ha="right",
         rotation_mode="anchor")

# Loop over data dimensions and create text annotations.
for i in range(len(stationData)):
    for j in range(len(monthData)):
        text = ax.text(j, i, dataAvailability[i, j],
                       ha="center", va="center", color="w")

#ax.set_title("Harvest of local farmers (in tons/year)")
fig.tight_layout()
plt.savefig('foo.pdf', dpi=600,facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=1.1,
        frameon=None, metadata=None)
plt.show()
