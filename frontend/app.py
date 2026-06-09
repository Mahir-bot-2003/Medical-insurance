"""
app.py  –  Streamlit frontend for Medical Insurance Cost Predictor
------------------------------------------------------------------
Make sure the FastAPI backend is running first:
    uvicorn backend.main:app --reload --port 8000

Then start this app:
    streamlit run frontend/app.py
"""

import requests
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏥 Insurance Cost Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Dark background ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        min-height: 100vh;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.04);
        border-right: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
    }

    /* ── Hero banner ── */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }
    .hero p {
        color: rgba(255,255,255,0.55);
        font-size: 1.05rem;
        max-width: 560px;
        margin: 0 auto;
    }

    /* ── Prediction card ── */
    .pred-card {
        background: linear-gradient(135deg, rgba(167,139,250,0.15) 0%, rgba(96,165,250,0.15) 100%);
        border: 1px solid rgba(167,139,250,0.35);
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        margin-top: 1rem;
    }
    .pred-label {
        color: rgba(255,255,255,0.6);
        font-size: 0.9rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .pred-amount {
        font-size: 3.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }
    .pred-sub {
        color: rgba(255,255,255,0.45);
        font-size: 0.85rem;
        margin-top: 0.4rem;
    }

    /* ── Info card ── */
    .info-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
    }
    .info-card h4 {
        color: #a78bfa;
        margin: 0 0 0.4rem;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .info-card p {
        color: rgba(255,255,255,0.7);
        margin: 0;
        font-size: 0.92rem;
        line-height: 1.5;
    }

    /* ── Risk badge ── */
    .badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.8rem;
        letter-spacing: 0.06em;
    }
    .badge-low   { background: rgba(52,211,153,0.2); color: #34d399; border: 1px solid rgba(52,211,153,0.4); }
    .badge-med   { background: rgba(251,191,36,0.2);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.4); }
    .badge-high  { background: rgba(248,113,113,0.2); color: #f87171; border: 1px solid rgba(248,113,113,0.4); }

    /* ── Metric boxes ── */
    .metric-row { display: flex; gap: 1rem; margin-top: 1.2rem; }
    .metric-box {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .metric-box .val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #60a5fa;
    }
    .metric-box .lbl {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.45);
        margin-top: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── Sidebar label ── */
    [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.75) !important;
        font-weight: 500 !important;
    }

    /* ── Predict button ── */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #7c3aed, #3b82f6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        cursor: pointer;
        transition: all 0.2s;
        margin-top: 0.5rem;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 24px rgba(124,58,237,0.45);
    }

    /* ── Error / warning boxes ── */
    .err-box {
        background: rgba(248,113,113,0.12);
        border: 1px solid rgba(248,113,113,0.35);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #fca5a5;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>🏥 Insurance Cost Predictor</h1>
        <p>Enter your details in the sidebar to get an instant estimate of your annual medical insurance charges powered by Machine Learning.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar Inputs ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='color:white;font-weight:700;margin-bottom:1.2rem;'>👤 Your Details</h2>",
        unsafe_allow_html=True,
    )

    age = st.slider("Age", min_value=18, max_value=100, value=35, step=1)

    sex = st.selectbox(
        "Biological Sex",
        options=["male", "female"],
        format_func=lambda x: "♂ Male" if x == "male" else "♀ Female",
    )

    bmi = st.slider(
        "BMI (Body Mass Index)",
        min_value=10.0,
        max_value=60.0,
        value=28.5,
        step=0.1,
        help="Normal: 18.5–24.9 | Overweight: 25–29.9 | Obese: ≥ 30",
    )

    children = st.slider(
        "Number of Children Covered",
        min_value=0,
        max_value=10,
        value=0,
        step=1,
    )

    smoker = st.selectbox(
        "Smoking Status",
        options=["no", "yes"],
        format_func=lambda x: "🚭 Non-smoker" if x == "no" else "🚬 Smoker",
    )

    region = st.selectbox(
        "Residential Region (US)",
        options=["northeast", "northwest", "southeast", "southwest"],
        format_func=lambda x: {
            "northeast": "🗺️ Northeast",
            "northwest": "🗺️ Northwest",
            "southeast": "🗺️ Southeast",
            "southwest": "🗺️ Southwest",
        }[x],
    )

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("⚡ Predict Insurance Cost", use_container_width=True)

# ── Helper: BMI category ───────────────────────────────────────────────────
def bmi_category(bmi_val):
    if bmi_val < 18.5:
        return "Underweight"
    elif bmi_val < 25:
        return "Normal"
    elif bmi_val < 30:
        return "Overweight"
    else:
        return "Obese"

def risk_badge(charge):
    if charge < 8000:
        return '<span class="badge badge-low">🟢 Low Cost</span>'
    elif charge < 20000:
        return '<span class="badge badge-med">🟡 Moderate Cost</span>'
    else:
        return '<span class="badge badge-high">🔴 High Cost</span>'

# ── Main panel ────────────────────────────────────────────────────────────
col_main, col_insights = st.columns([3, 2], gap="large")

with col_main:
    if predict_btn:
        payload = {
            "age": age,
            "sex": sex,
            "bmi": round(bmi, 1),
            "children": children,
            "smoker": smoker,
            "region": region,
        }

        with st.spinner("Computing your insurance estimate …"):
            try:
                resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                resp.raise_for_status()
                result = resp.json()
                charge = result["predicted_charge"]

                # ── Prediction card ────────────────────────────────────────
                badge_html = risk_badge(charge)
                st.markdown(
                    f"""
                    <div class="pred-card">
                        <div class="pred-label">Estimated Annual Insurance Cost</div>
                        <div class="pred-amount">${charge:,.0f}</div>
                        <div class="pred-sub">per year &nbsp;·&nbsp; USD</div>
                        {badge_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── Monthly breakdown ──────────────────────────────────────
                st.markdown(
                    f"""
                    <div class="metric-row">
                        <div class="metric-box">
                            <div class="val">${charge/12:,.0f}</div>
                            <div class="lbl">Monthly</div>
                        </div>
                        <div class="metric-box">
                            <div class="val">${charge/52:,.0f}</div>
                            <div class="lbl">Weekly</div>
                        </div>
                        <div class="metric-box">
                            <div class="val">${charge/365:,.1f}</div>
                            <div class="lbl">Daily</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── Model stats ────────────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption(
                    f"🔬 Model R² = **{result['model_r2']:.0%}** accuracy  |  "
                    f"RMSE ≈ **${result['model_rmse']:,.0f}**  |  "
                    f"Algorithm: **Linear Regression**"
                )

            except requests.exceptions.ConnectionError:
                st.markdown(
                    """
                    <div class="err-box">
                    ⚠️ <strong>Cannot connect to the API.</strong><br>
                    Make sure the FastAPI backend is running:<br>
                    <code>uvicorn backend.main:app --reload --port 8000</code>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            except requests.exceptions.HTTPError as e:
                st.markdown(
                    f'<div class="err-box">⚠️ API error: {e}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.markdown(
                    f'<div class="err-box">⚠️ Unexpected error: {e}</div>',
                    unsafe_allow_html=True,
                )

    else:
        # Placeholder state
        st.markdown(
            """
            <div class="pred-card" style="opacity:0.5;">
                <div class="pred-label">Estimated Annual Insurance Cost</div>
                <div class="pred-amount" style="color:rgba(255,255,255,0.3);">$ —,———</div>
                <div class="pred-sub">Fill in the sidebar and click Predict</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Insights panel ─────────────────────────────────────────────────────────
with col_insights:
    st.markdown(
        "<h3 style='color:white;font-weight:700;margin-bottom:1rem;'>📊 Key Insights</h3>",
        unsafe_allow_html=True,
    )

    bmi_cat = bmi_category(bmi)

    # BMI insight
    bmi_color = {"Underweight": "#60a5fa", "Normal": "#34d399", "Overweight": "#fbbf24", "Obese": "#f87171"}[bmi_cat]
    st.markdown(
        f"""
        <div class="info-card">
            <h4>⚖️ Your BMI</h4>
            <p>BMI of <strong style='color:{bmi_color}'>{bmi:.1f}</strong> is classified as
            <strong style='color:{bmi_color}'>{bmi_cat}</strong>.
            {'Higher BMI is correlated with elevated insurance costs.' if bmi >= 25 else 'Healthy BMI range keeps your premiums lower.'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Smoker insight
    smoker_txt = (
        "🚬 <strong style='color:#f87171'>Smoking is the single biggest cost driver</strong> — "
        "smokers pay on average <strong>$23,000 more</strong> per year."
        if smoker == "yes"
        else "🚭 Non-smoking status significantly <strong style='color:#34d399'>reduces your premium</strong>."
    )
    st.markdown(
        f'<div class="info-card"><h4>🚬 Smoking Impact</h4><p>{smoker_txt}</p></div>',
        unsafe_allow_html=True,
    )

    # Age insight
    age_txt = (
        "Older individuals typically face higher premiums as health risks increase with age."
        if age > 45
        else "Younger age groups generally benefit from lower insurance costs."
    )
    st.markdown(
        f'<div class="info-card"><h4>🎂 Age Factor</h4><p>{age_txt}</p></div>',
        unsafe_allow_html=True,
    )

    # Region insight
    region_notes = {
        "southeast": "The Southeast tends to have the <strong>highest average charges</strong> due to higher obesity rates.",
        "southwest": "The Southwest has moderately higher-than-average charges.",
        "northeast": "The Northeast has <strong>below-average charges</strong> in this dataset.",
        "northwest": "The Northwest has the <strong>lowest average charges</strong> among all regions.",
    }
    st.markdown(
        f'<div class="info-card"><h4>🗺️ Regional Trend</h4><p>{region_notes[region]}</p></div>',
        unsafe_allow_html=True,
    )

    # Children insight
    if children > 0:
        st.markdown(
            f'<div class="info-card"><h4>👶 Dependents</h4><p>You have <strong>{children} {"child" if children == 1 else "children"}</strong> covered. Each dependent adds a modest cost to your premium.</p></div>',
            unsafe_allow_html=True,
        )

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:rgba(255,255,255,0.25);font-size:0.8rem;'>"
    "Medical Insurance Cost Predictor · Linear Regression Model · Dataset: 1338 records · R² = 78%"
    "</p>",
    unsafe_allow_html=True,
)
