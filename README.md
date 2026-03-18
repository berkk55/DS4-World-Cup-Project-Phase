# DS4-World-Cup-Project-Phase

24.01.2026 - WorkShop  
⚽ Igniting Passion. Creating Champions.

Football is a game of emotion, but success is a game of numbers. In this project, our team (Valyo, Berk & Jean Philippe) analyzes historical World Cup data to decode the DNA of a champion.

Moving from opinion to evidence, we merge and analyze diverse Kaggle datasets to answer key questions:

🔍 **Evolution:** How has the game changed over decades?  
🏆 **Success Factors:** What statistically separates winners from the rest?  
🔮 **The Future:** What can history tell us about the expanded 2026 World Cup?

---

### Project Structure

```
DS4-World-Cup-Project-Phase/
├── analysis/          # Jupyter notebooks (data pipeline, EDA, modeling)
├── app/               # Streamlit web app (dashboard + predictions)
├── data/              # Datasets (raw, cleaned, ML-ready)
├── models/            # Trained models (.joblib)
├── guide.md           # Technical specification
├── requirements.txt   # Python dependencies
└── README.md
```

### Analysis Folder (Notebooks)

| Notebook | Purpose |
|----------|---------|
| **n0_data_collection_jpa** | Data collection and loading |
| **n1_cleaning_dataset_jpa** | Clean and prepare match data |
| **n2_EDA_jpa** | Exploratory data analysis (matches) |
| **n2_EDA_players_jpa** | EDA on player-level data |
| **n3_feature_engineering** | Base feature engineering → `ml_df.csv` |
| **n3.1_feature_engineering** | Player features → `ml_df_v2.csv` |
| **n3.2_feature_engineering** | Venue features → `ml_df_v4.csv` |
| **n4.21_training** | Train model v4 → `worldcup_model_v4.joblib` |
| **n4.4_distribution_shift** | Check train vs test distribution |
| **n4.4_leakage_audit** | Check for data leakage |
| **n5.2_prediction** | Evaluate v4 on 2022 matches |

**Model v4 pipeline (in order):** n3.1 → n3.2 → n4.21. Prerequisite: `n3_feature_engineering` must be run first.

### App Folder

- **app.py** – Main Streamlit entry point (Dashboard)
- **pages/** – Dashboard, Chat, 2026 Predictions
- **data/** – Prediction logic and model loading

---

## How to Run the App

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit App

From the project root:

```bash
streamlit run app/app.py
```

Or from the `app` folder:

```bash
cd app
streamlit run app.py
```

The app will open in your browser (typically `http://localhost:8501`).

### 3. What You'll See

- **Dashboard** – Historical World Cup stats, goals, attendance, champions
- **Chat** – Interactive Q&A
- **2026 Predictions** – Select a match and model to get outcome and score predictions

### 4. Required Data and Models

For predictions to work, ensure:

- `data/ml_df_v4.csv` exists (from n3.2)
- `models/worldcup_model_v4.joblib` exists (from n4.21)
- `data/2026_wc_data_v.csv` exists (2026 schedule)
- `data/team_rankings.csv` or `data/rankings.csv` exists (FIFA rankings)

---

## Quick Start for Evaluation

1. Run notebooks in order: **n3** → **n3.1** → **n3.2** → **n4.21**
2. Run `streamlit run app/app.py`
3. Open **2026 Predictions**, pick a match and model, then click **Predict**

---

## Key Concepts for Review

- **Score-first model:** Predicts goals, then derives win/draw/loss from the score
- **No leakage:** Features use only pre-match information (`_before`, `_diff`, etc.)
- **Time-aware split:** Train on 1930–2014, validate on 2018, test on 2022
- **Venue features:** `is_neutral_venue` and `home_advantage_strength` for host advantage
