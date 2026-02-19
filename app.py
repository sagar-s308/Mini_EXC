import streamlit as st
import pandas as pd
import pickle
import numpy as np


# ---------- Page config ----------
st.set_page_config(page_title="Cylinder Cost estimator for Mini Excavators", layout="wide")

# ---------- Uniform Small Input Box CSS ----------
st.markdown("""
    <style>
    /* Make ALL number input boxes same width */
    div[data-testid="stNumberInput"] input {
        width: 120px !important;
        padding: 6px !important;
        font-size: 19px !important;   /* Increased +5 */
        text-align: center;
        
    }

    /* Increase Selectbox font */
    div[data-testid="stSelectbox"] div {
        font-size: 14px !important;   /* Increased +5 */
    }

    /* Increase input labels */
    label {
        font-size: 14px !important;   /* Increased +5 */
    }

    /* Increase Metric value (Estimated Weight) */
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: bold;
    }

    /* Increase Metric label */
    div[data-testid="stMetricLabel"] {
        font-size: 18px !important;
    }

    /* Highlight Predicted Cost */
    .cost-card {
        background-color: #e8f4ff;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1f77ff;
        text-align: center;
        font-size: 25px !important;   /* Increased +5 */
        font-weight: bold;
        color: #003b8e;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Logo ----------
st.image("logo.png", width=250)


# ---------- Load model ----------
@st.cache_resource
def load_model():
    return pickle.load(open(r"./MiniExcmodel.pkl", "rb"))

model = load_model()


# ---------- Title ----------
st.title("Cylinder Cost estimator for Mini Excavators")


# ---------- Options ----------
APPLICATIONS = [
    "Arm Cylinder", "Boom Cylinder", "Bucket Cylinder",
    "Blade Cylinder", "Swing Cylinder",
]

CUSHIONS = ["NC", "CC", "CH", "CB"]


# ---------- Defaults ----------
DEFAULTS = {
    "tube_OD": 70,
    "bore": 60,
    "rod": 35,
    "stroke": 400,
    "closed_len": 650,
    "application": "Arm Cylinder",
    "cushion": "NC"
}

st.subheader("Enter Cylinder Technical Parameters")


# ---------- Layout ----------
left, right = st.columns([1.5, 2.1])


# ================= LEFT PANEL =================
with left:
    st.markdown("#### Dimensions")

    tube_OD = st.number_input("Tube OD (mm)", 0, 200, DEFAULTS["tube_OD"], 1)
    bore = st.number_input("Bore (mm)", 0, 200, DEFAULTS["bore"], 1)
    rod = st.number_input("Rod (mm)", 0, 200, DEFAULTS["rod"], 1)
    stroke = st.number_input("Stroke (mm)", 0, 2000, DEFAULTS["stroke"], 5)
    closed_len = st.number_input("Closed Length (mm)", 0, 2500, DEFAULTS["closed_len"], 5)


# ================= RIGHT PANEL =================
with right:
    st.markdown("#### Configuration")

    application = st.selectbox(
        "Application Type",
        APPLICATIONS,
        index=APPLICATIONS.index(DEFAULTS["application"])
    )

    cushion = st.selectbox(
        "Cushioning Type",
        CUSHIONS,
        index=CUSHIONS.index(DEFAULTS["cushion"])
    )


# ---------- Dynamic Weight Calculation ----------
weight = (np.pi / 4) * (0.00000785) * (
    tube_OD**2 * closed_len - (bore**2 - rod**2) * stroke
)

if weight < 0:
    st.warning("Estimated weight is negative. Please check geometry.")


# ---------- Prepare Model Input ----------
input_df = pd.DataFrame([{
    "Est. Wt (Kg)": weight,
    "Rod": rod,
    "Stroke": stroke,
    "Tube_OD": tube_OD,
    "Application": application,
    "Cushion Type": cushion
}])


# ---------- Prediction ----------
try:
    pred = model.predict(input_df)[0]

    st.markdown("### Dynamic Results")

    c1, c2 = st.columns([1, 1.2])

    # Weight
    c1.metric("Estimated Weight (Kg)", f"{weight:,.2f}")

    # Highlighted Cost
    with c2:
        st.markdown(
            f'<div class="cost-card">Predicted Cost<br>₹ {pred:,.2f}</div>',
            unsafe_allow_html=True
        )

    with st.expander("Show model input row"):
        st.dataframe(input_df, use_container_width=True)

except Exception as e:
    st.error("Prediction failed.")
    st.code(str(e))

