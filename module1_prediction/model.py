# module1_prediction/model.py
# ══════════════════════════════════════════════════════
# Module 1 — Student Risk Prediction
# Uses: sqlite3 + Pandas + NumPy + Scikit-learn
# ══════════════════════════════════════════════════════
 
import sqlite3
import pickle
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# ── Path to database and model file ───────────────────
# os.path makes sure the path works on any computer


BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, 'university.db')
MODEL_PATH= os.path.join(BASE_DIR, 'module1_prediction', 'model.pkl')


# ══════════════════════════════════════════════════════
# STEP 1 — Load data from SQLite
# ══════════════════════════════════════════════════════

def load_data():
    """
    Read students table from SQLite database.
    Returns a clean Pandas DataFrame.
    """
    conn = sqlite3.connect(DB_PATH)
 
    df = pd.read_sql("SELECT * FROM students", conn)
 
    conn.close()
 
    # Remove rows with empty values
    df = df.dropna()
 
    # Fill any remaining empty values with 0
    df = df.fillna(0)
 
    return df


# ══════════════════════════════════════════════════════
# STEP 2 — Train the model
# Call this ONCE to create model.pkl
# ══════════════════════════════════════════════════════
def train_model():
    """
    Train Random Forest on student data.
    Saves model to model.pkl file.
    Returns accuracy score.
    """
 
    # --- Load data ---
    df = load_data()
 
    print(f"Total students loaded: {len(df)}")
    print(f"At-risk students: {df['at_risk'].sum()}")
    print(f"Safe students: {(df['at_risk'] == 0).sum()}")
 
    # --- Features (X) ---
    # These are the 3 columns the model uses to predict
    X = df[['note', 'assiduite', 'participation']].values
    # X shape example: (200, 3)
    # Each row: [note, assiduite, participation]
    # Example:  [42.0, 55.0, 30.0]
 
    # --- Label (y) ---
    # This is what we want to predict: 0=safe, 1=at risk
    y = df['at_risk'].values
    # y example: [1, 0, 1, 0, 0, 1, ...]
 
    # --- Split: 80% train / 20% test ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,    # 20% for testing
        random_state=42   # same split every run
    )
 
    print(f"Training set: {len(X_train)} students")
    print(f"Test set:     {len(X_test)} students")
 
    # --- Train Random Forest ---
    model = RandomForestClassifier(
        n_estimators=100,   # 100 decision trees
        random_state=42     # reproducible results
    )
    model.fit(X_train, y_train)
 
    print("Model trained successfully!")
 
    # --- Check accuracy ---
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"Accuracy: {acc * 100:.1f}%")
 
    # --- Show feature importance ---
    features = ['note', 'assiduite', 'participation']
    importances = model.feature_importances_
    print("\nFeature importance:")
    for feat, imp in zip(features, importances):
        print(f"  {feat}: {imp * 100:.1f}%")
 
    # --- Save model to file ---
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
 
    print(f"\nModel saved to: {MODEL_PATH}")
 
    return round(acc * 100, 1)
 
 
# ══════════════════════════════════════════════════════
# STEP 3 — Predict all students
# Called by Flask route /api/predict
# ══════════════════════════════════════════════════════


def predict_all():
    """
    Load model and predict risk for all students.
    Returns a list of dicts ready for Flask jsonify.
    """
 
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print("model.pkl not found — training now...")
        train_model()
 
    # --- Load data ---
    df = load_data()
 
    # --- Features array for model ---
    X = df[['note', 'assiduite', 'participation']].values
 
    # --- Load saved model ---
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
 
    # --- Predict 0 or 1 for each student ---
    df['prediction'] = model.predict(X)
    # [1, 0, 1, 0, 0, 1, ...]
    # 1 = at risk   0 = safe
 
    # --- Calculate risk score (percentage) ---
    # predict_proba returns [[safe%, risk%], ...]
    # [:, 1] takes only the risk% column
    df['score'] = (
        model.predict_proba(X)[:, 1] * 100
    ).round(0).astype(int)
    # [87, 8, 92, 22, ...]
 
    # --- Add risk level label ---
    def get_level(score):
        if score >= 70:
            return 'A risque'
        elif score >= 40:
            return 'Moyen'
        else:
            return 'Safe'
 
    df['level'] = df['score'].apply(get_level)
 
    # --- Return only what frontend needs ---
    result = df[[
        'id',
        'nom',
        'filiere',
        'note',
        'assiduite',
        'participation',
        'at_risk',
        'prediction',
        'score',
        'level'
    ]].to_dict('records')
 
    return result


def at_risk_by_filiere():
    
    predictions = predict_all()
    info = sum(1 for s in predictions if s.get('prediction')==1 and s.get('filiere') == 'Informatique')
    math = sum(1 for s in predictions if s.get('prediction')==1 and s.get('filiere') == 'Mathématiques')
    ch = sum(1 for s in predictions if s.get('prediction')==1 and s.get('filiere') == 'Chimie')
    ph = sum(1 for s in predictions if s.get('prediction')==1 and s.get('filiere') == 'Physique')
    geo = sum(1 for s in predictions if s.get('prediction')==1 and s.get('filiere') == 'Géologie')
    biol = sum(1 for s in predictions if s.get('prediction')==1 and s.get('filiere') == 'Biologie')
    dic = {'Informatique':info,'Mathématiques':math,'Chimie':ch,'Physique':ph,'Géologie':geo,'Biologie':biol}
    sorted_dic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
    return sorted_dic 

def at_risk_percentages():
    data = at_risk_by_filiere()
    total = sum(data.values())

    percentages = {}
    for k, v in data.items():
        percentages[k] = round((v / total) * 100, 2) if total != 0 else 0

    return percentages


# ══════════════════════════════════════════════════════
# STEP 4 — Get statistics for dashboard
# ══════════════════════════════════════════════════════
def get_stats():
    """
    Returns summary statistics for the dashboard.
    """
 
    if not os.path.exists(MODEL_PATH):
        train_model()
 
    results = predict_all()
 
    at_risk = sum(1 for s in results if s['prediction'] == 1)
    safe    = sum(1 for s in results if s['prediction'] == 0)
    total   = len(results)
 
    # accuracy from model on test data
    df = load_data()
    X  = df[['note', 'assiduite', 'participation']].values
    y  = df['at_risk'].values
 
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
 
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    acc = accuracy_score(y_test, model.predict(X_test))
 
    # feature importance
    features    = ['note', 'assiduite', 'participation']
    importances = model.feature_importances_
    feat_imp    = {
        f: round(imp * 100, 1)
        for f, imp in zip(features, importances)
    }
 
    return {
        'total':        total,
        'at_risk':      at_risk,
        'safe':         safe,
        'accuracy':     round(acc * 100, 1),
        'feature_imp':  feat_imp
    }

# ══════════════════════════════════════════════════════
# RUN THIS FILE DIRECTLY TO TRAIN
# python module1_prediction/model.py
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("Training Module 1 — Student Risk Prediction")
    print("=" * 50)
    acc = train_model()
    print(f"\nDone! Final accuracy: {acc}%")
    print("\nTesting predict_all()...")
    results = predict_all()
    print(f"Predictions done for {len(results)} students")
    at_risk = sum(1 for s in results if s['prediction'] == 1)
    print(f"At risk: {at_risk}")
    print(f"Safe:    {len(results) - at_risk}")



