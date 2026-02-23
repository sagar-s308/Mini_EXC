import streamlit as st
import pandas as pd
import pickle
import numpy as np
from pathlib import Path

# ---------- Page config ----------
st.set_page_config(page_title="Cylinder Cost Estimator", layout="wide")

# ---------- Uniform Small Input Box CSS ----------
st.markdown("""
<style>
    /* ===== TITLE SIZE ===== */
    h1 {
        font-size: 40px !important;
        font-weight: 700;
    }

    /* Make ALL number input boxes same width */
    div[data-testid="stNumberInput"] input {
        width: 120px !important;
        padding: 6px !important;
        font-size: 17px !important;
        text-align: left;
    }

    /* Increase Selectbox font */
    div[data-testid="stSelectbox"] div {
        font-size: 14px !important;
    }
    
    div[data-testid="stNumberInput"] > label,
    div[data-testid="stSelectbox"] > label {
        font-size: 19px !important;
        font-weight: 600 !important;
        line-height: 1.2;
    }

    /* Increase Metric value (Estimated Weight) */
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: bold;
    }

    /* Increase Metric label */
    div[data-testid="stMetricLabel"] {
        font-size: 22px !important;
    }

    /* Highlight Predicted Cost */
    .cost-card {
        background-color: #e8f4ff;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1f77ff;
        text-align: center;
        font-size: 25px !important;
        font-weight: bold;
        color: #003b8e;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Logo ----------
st.image("logo.png", width=250)

# ---------- Title ----------
st.title("Cylinder Cost Estimator")

# ---------- Segments, Models, and Options ----------
SEGMENTS = ["Mini Excavator", "Material Handling (MH)"]

# Map each segment to a different model file (update names if needed)
MODEL_FILES = {
    "Mini Excavator": "./MiniExcmodel.pkl",
    "Material Handling (MH)": "./MH_xgb_model.pkl",    # <-- PLACE YOUR MH MODEL FILE HERE
}

# Segment-specific Application lists (customize MH as needed)
APPLICATIONS_BY_SEGMENT = {
    "Mini Excavator": [
        "Arm Cylinder", "Boom Cylinder", "Bucket Cylinder",
        "Blade Cylinder", "Swing Cylinder",
    ],
    "Material Handling (MH)": [
        # Example placeholders—replace with your MH application names
       " Boom / Jib / Implement",
        "Counterweight / Compensation",
        "Extension / Telescopic",
        "General / Misc",
        "Levelling / Auxiliary Control",
        "Lift / Hoist",
        "Outrigger / Stabilizer / Jack",
        "Steering / Positioning",
        "Tilt"

    ],
}

# Segment-specific defaults (adjust MH defaults if needed)
DEFAULTS_BY_SEGMENT = {
    "Mini Excavator": {
        "tube_OD": 70,
        "bore": 60,
        "rod": 35,
        "stroke": 400,
        "closed_len": 650,
        "application": "Arm Cylinder",
        "cushion": "NC"
    },
    "Material Handling (MH)": {
        "tube_OD": 80,
        "bore": 70,
        "rod": 40,
        "stroke": 450,
        "closed_len": 700,
        "application": "Lift Cylinder",
        "cushion": "NC",
        "equip_cat":"Telehandler"
    },
}
EQIP_MH = {
   
        "AWP",
        "Crane",
        "Forklift",
        "Other/Unknown",
        "Telehandler"

   
}

CUSHIONS = ["NC", "CC", "CH", "CB"]  # Keep same for both unless MH differs

# ---------- Segment Select (Top) ----------
with st.container():
    cseg1, cseg2 = st.columns([2.2, 1])
    with cseg1:
        segment = st.selectbox("Segment", SEGMENTS, index=0)
    with cseg2:
        st.write("")  # spacer

# Grab segment-specific resources
APP_LIST = APPLICATIONS_BY_SEGMENT[segment]
DEFAULTS = DEFAULTS_BY_SEGMENT[segment]
MODEL_PATH = MODEL_FILES[segment]
# EQUIP_LIST = DEFAULTS_BY_EQIP[segment]

# ---------- Model Loader ----------
@st.cache_resource(show_spinner=False)
def load_model(model_path: str):
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    with open(model_path, "rb") as f:
        return pickle.load(f)

# Try loading earliest to fail fast if model missing
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    st.error(f"Failed to load the model for '{segment}'.")
    st.code(str(e))
    st.stop()

st.subheader("Enter Cylinder Technical Parameters")

# ---------- Layout ----------
left, right = st.columns([1.5, 2.1])

# ================= LEFT PANEL =================
with left:
    st.markdown("#### Dimensions")

    tube_OD = st.number_input("Tube OD (mm)", 0, 300, DEFAULTS["tube_OD"], 1)
    bore = st.number_input("Bore (mm)", 0, 300, DEFAULTS["bore"], 1)
    rod = st.number_input("Rod (mm)", 0, 300, DEFAULTS["rod"], 1)
    stroke = st.number_input("Stroke (mm)", 0, 3000, DEFAULTS["stroke"], 5)
    closed_len = st.number_input("Closed Length (mm)", 0, 3500, DEFAULTS["closed_len"], 5)

# ================= RIGHT PANEL =================
with right:
    st.markdown("#### Application")

    application = st.selectbox(
        "Application Type",
        APP_LIST,
        index=APP_LIST.index(DEFAULTS["application"]) if DEFAULTS["application"] in APP_LIST else 0
    )

    cushion = st.selectbox(
        "Cushioning Type",
        CUSHIONS,
        index=CUSHIONS.index(DEFAULTS["cushion"]) if DEFAULTS["cushion"] in CUSHIONS else 0
    )
    if segment == "Material Handling (MH)":
        equip_cat = st.selectbox(
            "Equipment Category",
            EQIP_MH,
            # index = EQUIP_LIST.index()

        )

# ---------- Dynamic Weight Calculation ----------
# (Same formula as before; change if MH requires a different approach)
weight = (np.pi / 4) * (0.00000785) * (
    tube_OD**2 * closed_len - (bore**2 - rod**2) * stroke
)

if weight < 0:
    st.warning("Estimated weight is negative. Please check geometry.")

# ---------- Prepare Model Input (per-segment schema) ----------
# If your MH model expects different column names, set them here conditionally.
if segment == "Mini Excavator":
    input_df = pd.DataFrame([{
        "Est. Wt (Kg)": weight,
        "Rod": rod,
        "Stroke": stroke,
        "Tube_OD": tube_OD,
        "Application": application,
        "Cushion Type": cushion
    }])
else:  # Material Handling (MH)
    # Example: using the same schema. Change keys to match your MH model training columns.
    input_df = pd.DataFrame([{
        "Est. Wt": weight,
        "ClosedLength": closed_len,
        "Rod_OD": rod,
        "Stroke": stroke,
        "Bore(Tube_ID)": bore,
        "Tube_OD": tube_OD,
        "Application": application,
        "Cushion Type": cushion,
        "Equipment_Category":equip_cat
    }]) 

# ---------- Prediction ----------
try:
    pred = model.predict(input_df)[0]

    st.markdown("### Dynamic Results")
    c1, c2 = st.columns([1, 1.2])

    # Weight metric
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
