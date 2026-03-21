import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from pathlib import Path

#Didnt work : df = pd.read_csv("../test_analysis/ml_df_test_bab.csv")

skript_ordner = Path(__file__).parent
csv_pfad = skript_ordner / ".." / "test_analysis" / "ml_df_test_bab.csv"
df = pd.read_csv(csv_pfad.resolve())

df_train = df[df["year"] <= 2018]
prediction = df[df['year'] == 2022]

y_train = df_train["result_target"]
y_test = prediction["result_target"]

relevant_columns = [
    'elo_diff', 'win_rate_diff', 'goal_diff_diff', 'form_diff', 
    'goals_per_match_diff', 'conceded_per_match_diff',
    'home_elo_before', 'away_elo_before',
    'home_total_win_rate_before', 'away_total_win_rate_before',
    'home_goal_diff_per_match_before', 'away_goal_diff_per_match_before',
    'home_last5_win_rate', 'away_last5_win_rate',
    'home_last5_goal_diff', 'away_last5_goal_diff',
    'home_tournaments_played_before', 'away_tournaments_played_before',
    'home_has_won_world_cup_before', 'away_has_won_world_cup_before',
    'home_is_defending_champion', 'away_is_defending_champion'
]

x_train = df_train[relevant_columns].select_dtypes(exclude=['object'])
x_test = prediction[relevant_columns].select_dtypes(exclude=['object'])

optimized_forest = RandomForestClassifier(
    n_estimators=300,            
    max_depth=3,                 
    max_features="sqrt",        
    min_samples_leaf= 3,         
    class_weight= "balanced",    
    random_state=42,
    n_jobs=-1                    
)

optimized_forest.fit(x_train, y_train)
y_pred_optimized_forest = optimized_forest.predict(x_test)

print("Classification Report for the optimized random forest model: \n" , classification_report(y_test, y_pred_optimized_forest))