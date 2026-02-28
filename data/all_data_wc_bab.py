# %%
import pandas as pd

df_old_wm_cups = pd.read_csv('c:/Users/pberk/OneDrive/Dokumente/Techlabs_Project_Phase/DS4-World-Cup-Project-Phase/data/cleaned_project_dataset.csv')
df_2026 = pd.read_csv('c:/Users/pberk/OneDrive/Dokumente/Techlabs_Project_Phase/DS4-World-Cup-Project-Phase/data/2026_wc_data_v.csv') 

df_all_cups = pd.concat([df_old_wm_cups, df_2026], ignore_index=True)

print(df_all_cups)



# %%
