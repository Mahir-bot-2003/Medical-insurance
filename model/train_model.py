"""
train_model.py
--------------
Reproduces the notebook training pipeline and saves the fitted model
plus the exact feature column list to model/insurance_model.pkl.

Run from the project root:
    python model/train_model.py
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "insurance.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "insurance_model.pkl")

# ── Load data ──────────────────────────────────────────────────────────────
print("[INFO] Loading data from:", DATA_PATH)
df = pd.read_csv(DATA_PATH)
print(f"       Shape: {df.shape}")

# ── Preprocess ─────────────────────────────────────────────────────────────
# One-hot encode categorical columns (drop_first to avoid multicollinearity)
df_encoded = pd.get_dummies(df, columns=["sex", "smoker", "region"], drop_first=True)

# Feature matrix and target vector
feature_cols = [c for c in df_encoded.columns if c != "charges"]
X = df_encoded[feature_cols]
y = df_encoded["charges"]

print(f"       Feature columns ({len(feature_cols)}): {feature_cols}")

# ── Train / test split (80 / 20, seed = 42) ────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# ── Train ──────────────────────────────────────────────────────────────────
print("\n[INFO] Training Linear Regression ...")
model = LinearRegression()
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
print(f"       RMSE : ${rmse:,.2f}")
print(f"       R2   : {r2:.4f}")

# ── Save ───────────────────────────────────────────────────────────────────
os.makedirs(MODEL_DIR, exist_ok=True)
payload = {
    "model": model,
    "feature_cols": feature_cols,
    "rmse": rmse,
    "r2": r2,
}
joblib.dump(payload, MODEL_PATH)
print(f"\n[OK]  Model saved to: {MODEL_PATH}")
