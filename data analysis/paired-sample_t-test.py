import pandas as pd
from scipy.stats import ttest_rel

# Load data
df = pd.read_csv('participants_gaze_data.csv')

# Select the two sets of data to be compared
data1 = df['Domain Consistent Gaze Time (s)']
data2 = df['Domain Inconsistent Gaze Time (s)']

#Perform a paired-sample t-test
stat, p = ttest_rel(data1, data2)


print('statistic=%.3f, p=%.3f' % (stat, p))

# Judging by the p-value
alpha = 0.05
if p > alpha:
    print('No significant difference between the two groups of data (Hypothesis could not be rejected)')
else:
    print('There is a significant difference between the two groups of data (Reject the hypothesis)')
