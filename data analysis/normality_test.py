import pandas as pd
from scipy.stats import shapiro

# Load data
df = pd.read_csv('participants_gaze_data.csv')

# Select the columns to test, e.g. 'Domain Consistent Gaze Time (s)'
data = df['Domain Inconsistent Gaze Time (s)']

# Perform the Shapiro-Wilk normality test
stat, p = shapiro(data)

# output result
print('statistic=%.3f, p=%.3f' % (stat, p))

# Determining normality based on p-value
alpha = 0.05
if p > alpha:
    print('Sample data is normally distributed (hypothesis cannot be rejected)')
else:
    print('Sample data is not normally distributed (Reject the hypothesis)')
