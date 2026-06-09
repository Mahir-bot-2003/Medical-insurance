"""
main.py  –  FastAPI backend for Medical Insurance Cost Prediction
-----------------------------------------------------------------
Start with:
    uvicorn backend.main:app --reload --port 8000

Interactive docs:
    http://localhost:8000/docs
"""

import os
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Load model ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "insurance_model.pkl")

try:
    payload = joblib.load(MODEL_PATH)
    model = payload["model"]
    FEATURE_COLS = payload["feature_cols"]
    MODEL_RMSE = payload["rmse"]
    MODEL_R2 = payload["r2"]
    print(f"[OK]  Model loaded  |  R2 = {MODEL_R2:.4f}  |  RMSE = ${MODEL_RMSE:,.2f}")
except FileNotFoundError:
    raise RuntimeError(
        f"Model file not found at {MODEL_PATH}. "
        "Run `python model/train_model.py` first."
    )

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="🏥 Medical Insurance Cost Predictor",
    description=(
        "Predict annual medical insurance charges based on personal attributes.\n\n"
        "**Model**: Linear Regression  |  "
        f"**R²**: {MODEL_R2:.2f}  |  "
        f"**RMSE**: ${MODEL_RMSE:,.0f}"
    ),
    version="1.0.0",
)

# Allow Streamlit (or any front-end) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ────────────────────────────────────────────────────────────────
class InsuranceInput(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Age of the beneficiary (18-100)", example=35)
    sex: Literal["male", "female"] = Field(..., description="Gender", example="male")
    bmi: float = Field(..., ge=10.0, le=60.0, description="Body Mass Index (10-60)", example=28.5)
    children: int = Field(..., ge=0, le=10, description="Number of children covered (0-10)", example=2)
    smoker: Literal["yes", "no"] = Field(..., description="Smoking status", example="no")
    region: Literal["northeast", "northwest", "southeast", "southwest"] = Field(
        ..., description="Residential region in the US", example="northeast"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 35,
                    "sex": "male",
                    "bmi": 28.5,
                    "children": 2,
                    "smoker": "no",
                    "region": "northeast",
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    predicted_charge: float = Field(..., description="Estimated annual insurance charge in USD")
    currency: str = "USD"
    model_r2: float = Field(..., description="Model R² score on test set")
    model_rmse: float = Field(..., description="Model RMSE on test set (USD)")
    input_summary: dict = Field(..., description="Echo of the input for reference")


# ── Helpers ────────────────────────────────────────────────────────────────
def build_feature_row(data: InsuranceInput) -> pd.DataFrame:
    """
    Convert an InsuranceInput into the same one-hot encoded DataFrame
    that the LinearRegression model was trained on.
    """
    raw = {
        "age": data.age,
        "bmi": data.bmi,
        "children": data.children,
        "sex": data.sex,
        "smoker": data.smoker,
        "region": data.region,
    }
    df_raw = pd.DataFrame([raw])

    # One-hot encode exactly as in training (drop_first=True)
    df_enc = pd.get_dummies(df_raw, columns=["sex", "smoker", "region"], drop_first=True)

    # Align with training feature columns (fill missing dummies with 0)
    df_enc = df_enc.reindex(columns=FEATURE_COLS, fill_value=0)
    return df_enc


# ── Routes ─────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Medical Insurance Cost Predictor",
        "status": "running",
        "version": "1.0.0",
        "model": "Linear Regression",
        "r2_score": round(MODEL_R2, 4),
        "rmse_usd": round(MODEL_RMSE, 2),
        "docs": "/docs",
        "predict": "/predict",
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(data: InsuranceInput):
    """
    Predict the annual medical insurance charge for a given individual.

    - **age**: 18–100
    - **sex**: male | female
    - **bmi**: Body Mass Index (10–60)
    - **children**: 0–10
    - **smoker**: yes | no
    - **region**: northeast | northwest | southeast | southwest
    """
    try:
        feature_row = build_feature_row(data)
        prediction = float(model.predict(feature_row)[0])
        # Ensure prediction is non-negative (model can theoretically go negative)
        prediction = max(prediction, 0.0)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return PredictionResponse(
        predicted_charge=round(prediction, 2),
        model_r2=round(MODEL_R2, 4),
        model_rmse=round(MODEL_RMSE, 2),
        input_summary=data.model_dump(),
    )
