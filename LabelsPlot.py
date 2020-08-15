import numpy as np
import pandas as pd
import pickle
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sklearn
from sklearn import metrics
from sklearn.cluster import KMeans

# Read data from file and create dataframe
labels_file = open(r"C:\Users\victoria.alkin\Documents\Labeling Meshes 2\labels.pkl","rb")
labels_db = pickle.load(labels_file)
labels_file.close()
labels_df = pd.DataFrame(labels_db)
labels_df.to_csv(r"C:\Users\victoria.alkin\Documents\Labeling Meshes 2\unpickled_labels_test.csv")

for i in range(len(labels_df)):
    ptcolor = ""
    if labels_df.iloc[i,4] == '1':
        ptcolor = "red"
    if labels_df.iloc[i,4] == '2':
        ptcolor = "limegreen"
    if labels_df.iloc[i,4] == '3':
        ptcolor = "gold"
    if labels_df.iloc[i,4] == '4':
        ptcolor = "orange"
    if labels_df.iloc[i,4] == '5':
        ptcolor = "lightcoral"
    if labels_df.iloc[i,4] == '6':
        ptcolor = "palegreen"
    if labels_df.iloc[i,4] == '7':
        ptcolor = "maroon"
    if labels_df.iloc[i,4] == '8':
        ptcolor = "darkgreen"
    if labels_df.iloc[i,4] == '9':
        ptcolor = "slategrey"
    x = labels_df.iloc[i,0]
    y = labels_df.iloc[i,1]
    plt.scatter(x, y, color = ptcolor, s=25)

spine_patch = mpatches.Patch(color = "red", label = "spine")
shaft_patch = mpatches.Patch(color = "limegreen", label = "shaft")
soma_patch = mpatches.Patch(color = "gold", label = "soma")
ais_patch = mpatches.Patch(color = "orange", label = "proximal process")
partialspine_patch = mpatches.Patch(color = "lightcoral", label = "partial spine")
partialshaft_patch = mpatches.Patch(color = "palegreen", label = "partial shaft")
mergedspine_patch = mpatches.Patch(color = "maroon", label = "merged spine")
mergedshaft_patch = mpatches.Patch(color = "darkgreen", label = "merged shaft")
unknown_patch = mpatches.Patch(color = "slategrey", label = "unknown")
plt.legend(handles = [spine_patch, shaft_patch, soma_patch, ais_patch, partialspine_patch, partialshaft_patch, mergedspine_patch, mergedshaft_patch, unknown_patch], fontsize = 'x-small')
plt.show()