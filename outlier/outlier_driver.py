#http://scikit-learn.org/stable/auto_examples/covariance/plot_outlier_detection.html#sphx-glr-auto-examples-covariance-plot-outlier-detection-py
import pandas as pd
#import googleapi
import numpy as np
import argparse
import pdb
import outlier
# if __name__ == '__main__':
import scipy.io
import pandas as pd

data = scipy.io.loadmat('annthyroid.mat')
df = pd.DataFrame(data['X'])
df = outlier.out(df)
print df
print df.groupby('svm_class').count()


import matplotlib.pyplot as plt

plt.scatter(df.iloc[:,2], df.iloc[:,3],c=df['forest_class'])
plt.colorbar()
plt.show()
