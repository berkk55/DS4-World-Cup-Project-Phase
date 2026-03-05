
import pandas as pd

df_old_wm_cups = pd.read_csv('data/cleaned_project_dataset.csv')
df_2026 = pd.read_csv('data/2026_wc_data_v.csv') 

df_all_cups = pd.concat([df_old_wm_cups, df_2026], ignore_index=True)

df_all_cups.to_csv('data/all_cups_combined.csv', index=False)

print(df_all_cups)




