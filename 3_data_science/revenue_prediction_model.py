"""
=============================================================================
STAGE 3: DATA SCIENCE (MACHINE LEARNING & PREDICTIVE MODELING)
Project: Bandung Gastronomy Intelligence
Module: Random Forest Revenue Prediction & Feature Importance
Author: Rifasa Hadiarto (Data Scientist)
=============================================================================
"""

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

def run_data_science():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'bandung_culinary_clean_all.csv')
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print(">>> Starting Data Science Machine Learning Pipeline...")
    print(f"[*] Loading dataset from: {os.path.basename(csv_path)}")

    df = pd.read_csv(csv_path)

    # 1. Feature Selection
    features = ['kategori_kuliner', 'zona_kawasan', 'rentang_harga', 'kapasitas_kursi', 'skor_rating', 'jumlah_ulasan']
    target = 'estimasi_omzet_bulanan_juta'

    X = df[features]
    y = df[target]

    categorical_features = ['kategori_kuliner', 'zona_kawasan', 'rentang_harga']
    numeric_features = ['kapasitas_kursi', 'skor_rating', 'jumlah_ulasan']

    # 2. Preprocessing & Modeling Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_features),
            ('num', 'passthrough', numeric_features)
        ]
    )

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12))
    ])

    # 3. Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"[*] Training on {len(X_train):,} samples, testing on {len(X_test):,} samples...")

    # 4. Model Training
    model_pipeline.fit(X_train, y_train)

    # 5. Evaluation
    y_pred = model_pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)

    print("\n--- [MODEL PERFORMANCE EVALUATION] ---")
    print(f"[*] Algorithm: Random Forest Regressor (100 Trees)")
    print(f"[*] R-Squared (R2 Score): {r2:.4f} (Explains {r2*100:.1f}% of revenue variance)")
    print(f"[*] Mean Absolute Error (MAE): Rp {mae:.2f} Juta")
    print(f"[*] Root Mean Squared Error (RMSE): Rp {rmse:.2f} Juta")

    # 6. Feature Importance Extraction
    encoder = model_pipeline.named_steps['preprocessor'].named_transformers_['cat']
    cat_feature_names = encoder.get_feature_names_out(categorical_features)
    all_feature_names = list(cat_feature_names) + numeric_features

    importances = model_pipeline.named_steps['regressor'].feature_importances_
    fi_df = pd.DataFrame({
        'Feature': all_feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)

    print("\n--- [TOP 5 REVENUE DRIVER FEATURES (FEATURE IMPORTANCE)] ---")
    print(fi_df.head(6).to_string(index=False))

    # 7. Real-World Business Scenario Prediction
    print("\n--- [SCENARIO SIMULATION FOR INVESTOR] ---")
    scenario_1 = pd.DataFrame([{
        'kategori_kuliner': 'Western Bistro & Casual Dining',
        'zona_kawasan': 'Koridor Paskal - Sudirman (Food Market & Asian)',
        'rentang_harga': 'Mid-Range (Rp 35k - 75k)',
        'kapasitas_kursi': 60,
        'skor_rating': 4.5,
        'jumlah_ulasan': 350
    }])
    pred_1 = model_pipeline.predict(scenario_1)[0]
    print(f"Scenario 1: Western Bistro di Paskal (60 kursi, rating 4.5)")
    print(f"   -> Prediksi Omzet: Rp {pred_1:.2f} Juta / bulan")

    scenario_2 = pd.DataFrame([{
        'kategori_kuliner': 'Coffee Shop & Roastery',
        'zona_kawasan': 'Koridor Riau - Progo (Pusat Cafe Lifestyle)',
        'rentang_harga': 'Budget Friendly (< Rp 35k)',
        'kapasitas_kursi': 35,
        'skor_rating': 4.2,
        'jumlah_ulasan': 120
    }])
    pred_2 = model_pipeline.predict(scenario_2)[0]
    print(f"Scenario 2: Coffee Shop Budget di Riau (35 kursi, rating 4.2)")
    print(f"   -> Prediksi Omzet: Rp {pred_2:.2f} Juta / bulan")

    # Save feature importances
    fi_df.to_csv(os.path.join(output_dir, 'feature_importance_revenue.csv'), index=False)
    print(f"\n[SUCCESS] Feature importances exported to: {output_dir}")

if __name__ == '__main__':
    run_data_science()
