import pandas as pd

df = pd.read_csv('iclr2024_raw.csv')
df_filtered = df[df['Mean'] >= 5.2]
df_sorted = df_filtered.sort_values(by='Mean', ascending=False)

# Write the sorted DataFrame back to a CSV file
df_sorted.to_csv('iclr2024_full.csv', index=False)