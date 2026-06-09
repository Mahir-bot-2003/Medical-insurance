# Medical-insurance
# Insurance Cost Prediction using Linear Regression  

## 📌 Introduction  
This project predicts **individual medical insurance costs** based on personal attributes such as age, BMI, smoking status, and region. By applying **Linear Regression**, the goal is to understand the factors influencing insurance premiums and build a predictive model that estimates charges accurately.  
---
DEMO LINK - https://medical-insurance-predict.streamlit.app/

## 📂 Dataset  
The project uses the **insurance.csv** dataset containing **1338 rows** and the following columns:  

- **age**: Age of the primary beneficiary  
- **sex**: Gender (male, female)  
- **bmi**: Body Mass Index (BMI)  
- **children**: Number of children covered by insurance  
- **smoker**: Smoking status (yes, no)  
- **region**: Residential area in the US (northeast, southeast, southwest, northwest)  
- **charges**: Individual medical costs (target variable)  

---

## 🔄 Project Workflow  
1. **Data Loading & Exploration**  
   - Load data using pandas  
   - Inspect structure with `.info()` and `.describe()`  

2. **Exploratory Data Analysis (EDA)**  
   - Visualizations (seaborn & matplotlib)  
   - Key insights:  
     - Charges are right-skewed  
     - Smokers have significantly higher costs  
     - Costs rise with age (especially for smokers)  

3. **Data Preprocessing**  
   - Encode categorical variables (`sex`, `smoker`, `region`) using one-hot encoding  

4. **Model Training**  
   - Split dataset into training (80%) and testing (20%)  
   - Train a **Linear Regression** model using scikit-learn  

5. **Model Evaluation**  
   - **RMSE**: 5796.28  
   - **R² Score**: 0.78 (model explains 78% of variability in charges)  

---

## 📊 Results  
- **RMSE**: 5796.28  
- **R² Score**: 0.78  
- Smoking status and age are the most significant predictors of insurance costs.  

---

## ✨ Features  
- Predicts insurance charges based on personal factors  
- End-to-end pipeline: data exploration → preprocessing → training → evaluation  
- Visual analysis to identify key patterns in insurance costs  

---

## Deployment — FastAPI + Streamlit

After building the ML model in the notebook, I took it a step further and **deployed it as a real web application** using **FastAPI** (backend API) and **Streamlit** (interactive frontend UI).

---

## What I Learned & How I Understood the Concepts

### 1. 🔧 What is FastAPI?

FastAPI is a modern Python web framework for building **REST APIs** — essentially a server that listens for HTTP requests and returns responses (usually JSON).

Before FastAPI, I thought of a "server" as something complicated. FastAPI made it click by being just Python:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}
```

That's it — a working web server. The `@app.get("/")` decorator tells FastAPI: *"when someone sends a GET request to `/`, run this function and return what it returns."*

---

### 2. 📦 Pydantic — Automatic Input Validation

One of the first things I learned is that APIs need to validate inputs before processing them. FastAPI uses **Pydantic models** for this:

```python
from pydantic import BaseModel, Field
from typing import Literal

class InsuranceInput(BaseModel):
    age:      int   = Field(..., ge=18, le=100)   # must be between 18 and 100
    sex:      Literal["male", "female"]            # only these two values allowed
    bmi:      float = Field(..., ge=10.0, le=60.0)
    smoker:   Literal["yes", "no"]
    region:   Literal["northeast", "northwest", "southeast", "southwest"]
```

**Key insight:** If someone sends `age: 999` or `sex: "robot"`, FastAPI automatically rejects it with a clear error — I don't write any validation logic myself. Pydantic handles it all.

---

### 3. How a POST Request Works — The Predict Endpoint

The core of the project is the `/predict` endpoint. Learning how POST requests work was the biggest "aha" moment:

```python
@app.post("/predict")
def predict(data: InsuranceInput):
    # 1. data is already validated by Pydantic
    # 2. convert the input to the same format the model was trained on
    feature_row = build_feature_row(data)
    # 3. run the ML model
    prediction = model.predict(feature_row)[0]
    return {"predicted_charge": round(prediction, 2)}
```

**What I understood:** A POST request is like filling out a form and submitting it. The "form data" arrives as JSON in the request body. FastAPI parses it, Pydantic validates it, and my function receives a clean Python object.

---

### 4. Saving and Loading the Model with joblib

I learned that you can't just use a model object from a Jupyter notebook in a web server — you need to **serialize** (save) it to a file and **deserialize** (load) it when the server starts:

```python
import joblib

# In train_model.py — save after training
joblib.dump({"model": model, "feature_cols": feature_cols}, "insurance_model.pkl")

# In main.py — load once at server startup
payload = joblib.load("insurance_model.pkl")
model = payload["model"]
```

**Key insight:** The model is loaded **once at startup**, not on every request. This makes predictions fast (milliseconds), since loading a model from disk is slow but predicting is instant.

---

### 5. 🎯 The One-Hot Encoding Problem

This was a tricky concept. The model was trained on encoded columns like `sex_male`, `smoker_yes`, `region_northwest` — not raw strings like `"male"` or `"northeast"`. So every prediction request must go through the **exact same encoding**:

```python
def build_feature_row(data):
    df = pd.DataFrame([{"age": data.age, "sex": data.sex, ...}])
    df_enc = pd.get_dummies(df, columns=["sex","smoker","region"], drop_first=True)
    # CRITICAL: align to the exact same columns the model was trained on
    df_enc = df_enc.reindex(columns=FEATURE_COLS, fill_value=0)
    return df_enc
```

**What I understood:** If the input is `region="northeast"`, none of the `region_*` dummy columns will be 1 (northeast is the dropped reference category). The `reindex(..., fill_value=0)` step handles this by filling any missing columns with 0 — matching exactly what the training data looked like.

---

### 6. CORS — Letting Streamlit Talk to FastAPI

When Streamlit (running on port `8501`) calls FastAPI (running on port `8000`), the browser blocks cross-origin requests by default. I learned about **CORS middleware** to allow this:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

**What I understood:** Browsers have a security rule that stops one website from calling another (e.g. `localhost:8501` calling `localhost:8000`). CORS middleware adds special response headers that tell the browser "this is allowed."

---

### 7. Streamlit — Building the UI

Streamlit turned the API into a real app. The key thing I learned is that Streamlit is just Python — you write Python and it renders a webpage:

```python
import streamlit as st
import requests

age = st.slider("Age", 18, 100, 35)           # renders a slider
smoker = st.selectbox("Smoker?", ["yes","no"]) # renders a dropdown

if st.button("Predict"):
    resp = requests.post("http://localhost:8000/predict", json={"age": age, ...})
    charge = resp.json()["predicted_charge"]
    st.write(f"Estimated cost: ${charge:,.0f}")
```

**Key insight:** Streamlit re-runs the entire script from top to bottom every time the user interacts with the UI. This is different from traditional web frameworks, but makes it very simple to build interactive ML demos.

---

### 8. 🏗️ The Full Architecture

The biggest learning was understanding how all three pieces connect:

```
insurance.csv
     │
     ▼  train_model.py
insurance_model.pkl
     │
     ▼  loaded at startup
FastAPI (port 8000)  ←── POST /predict ←── Streamlit (port 8501)
                                                   ▲
                                              User's Browser
```

**What I understood:** These are **two separate processes** that communicate over HTTP — the same protocol your browser uses to load websites. This means the FastAPI backend could be called by a mobile app, a React frontend, or a curl command — not just Streamlit.

---

## 🗂️ New Project Structure

```
Medical-insurance/
├── insurance.csv              ← Dataset
├── Insurance.ipynb            ← Original EDA + model notebook
├── requirements.txt           ← All dependencies
│
├── model/
│   └── train_model.py         ← Trains & saves the model as .pkl
│
├── backend/
│   └── main.py                ← FastAPI REST API server
│
└── frontend/
    └── app.py                 ← Streamlit web UI
```

---

## ▶️ How to Run

**Step 1 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2 — Train and save the model**
```bash
python model/train_model.py
```

**Step 3 — Start the FastAPI backend** *(Terminal 1)*
```bash
python -m uvicorn backend.main:app --port 8000 --reload
# API running at:     http://localhost:8000
# Swagger docs at:    http://localhost:8000/docs
```

**Step 4 — Start the Streamlit frontend** *(Terminal 2)*
```bash
python -m streamlit run frontend/app.py
# UI running at:      http://localhost:8501
```

---

## 🛠️ New Requirements

```
fastapi
uvicorn[standard]
streamlit
requests
joblib
pandas
numpy
scikit-learn
```


