import pandas as pd
import numpy as np

df = pd.read_csv("data/world_tourism_sample.csv")
time_col = "year"
category_col = "country"
value_col = "arrivals_millions"

df_pivot = df.pivot(index=time_col, columns=category_col, values=value_col)
print(df_pivot.head())

steps = 10
new_idx = []
orig_idx = df_pivot.index.tolist()
for i in range(len(orig_idx) - 1):
    new_idx.extend(np.linspace(orig_idx[i], orig_idx[i+1], steps, endpoint=False))
new_idx.append(orig_idx[-1])

df_pivot = df_pivot.reindex(pd.Index(new_idx, name=time_col)).interpolate(method='linear')
print(df_pivot.head(15))

df_melt = df_pivot.reset_index().melt(id_vars=time_col, var_name=category_col, value_name=value_col)
print(df_melt.head())
