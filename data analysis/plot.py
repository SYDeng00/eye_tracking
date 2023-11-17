import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ptitprince as pt

# retrieve data
df = pd.read_csv('participants_gaze_data.csv')

# In order to perform the visualization of the paired samples t-test, we need data in long format
df_long = df.melt(id_vars=['Participant'], 
                  value_vars=['Domain Consistent Gaze Time (s)', 'Domain Inconsistent Gaze Time (s)'],
                  var_name='Condition', value_name='Gaze Time (s)')

# Boxplot - showing the distribution of two conditions
plt.figure(figsize=(10, 6))
sns.boxplot(x='Condition', y='Gaze Time (s)', data=df_long)
plt.title('Box Plot of Gaze Times under Two Conditions')
plt.show()

# Scatterplot - shows how each participant performed in both conditions
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Domain Consistent Gaze Time (s)', y='Domain Inconsistent Gaze Time (s)', data=df)
plt.title('Scatter Plot of Gaze Times for Each Participant')
plt.xlabel('Consistent Gaze Time (s)')
plt.ylabel('Inconsistent Gaze Time (s)')
plt.show()

# Difference Plot - shows the difference between the two conditions for each participant
df['Difference'] = df['Domain Consistent Gaze Time (s)'] - df['Domain Inconsistent Gaze Time (s)']
plt.figure(figsize=(10, 6))
sns.barplot(x='Participant', y='Difference', data=df)
plt.title('Difference in Gaze Time for Each Participant')
plt.xticks(rotation=90)  # Rotate X-axis labels for better readability
plt.show()

# Use the previous long form datadf_long
plt.figure(figsize=(10, 6))

# Create a raincloud plot
ax = pt.RainCloud(x='Condition', y='Gaze Time (s)', data=df_long, palette="Set2", bw=.2,
                  width_viol=.6, orient='h', alpha=.65, dodge=True, pointplot=True)

plt.title('Raincloud Plot of Gaze Times under Two Conditions')
plt.show()