import pandas as pd
import numpy as np

# Read the original data
df = pd.read_csv("data/world_tourism_sample.csv")

# Ensure years are numeric
df['year'] = pd.to_numeric(df['year'])

# Pivot the data
df_pivot = df.pivot(index='year', columns='country', values='arrivals_millions')

# Reindex to have every year from min to max
min_year = int(df['year'].min())
max_year = int(df['year'].max())
new_index = pd.Index(range(min_year, max_year + 1), name='year')
df_pivot = df_pivot.reindex(new_index)

# Interpolate missing years linearly
df_pivot = df_pivot.interpolate(method='linear')

# Melt back to long format
df_melt = df_pivot.reset_index().melt(id_vars='year', var_name='country', value_name='arrivals_millions')

# Sort appropriately
df_melt = df_melt.sort_values(['country', 'year']).reset_index(drop=True)

# Save back to CSV
df_melt.to_csv("data/world_tourism_sample.csv", index=False)
print("Data updated to be year-by-year.")
