import streamlit as st
import pandas as pd
import pickle
import numpy as np

# ---------- Logo ----------
st.image("logo.png", width=250)   # keep logo.png in same folder

# ---------- Page config ----------
st.set_page_config(page_title="Cylinder Cost estimator for Mini Excavators", layout="wide")

# ---------- Load model ----------
model = pickle.load(open(r"./MiniExcmodel.pkl", "rb"))

# ---------- Titles ----------
st.title("Cylinder Cost estimator for Mini Excavators")


# ---------- Options ----------
APPLICATIONS = [
    "Arm Cylinder","Boom Cylinder","Bucket Cylinder","Blade Cylinder","Swing Cylinder",
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
col1, col2 = st.columns(2)

with col1:
    tube_OD = st.number_input("Tube OD (mm)", min_value=0, max_value=200, value=DEFAULTS["tube_OD"], step=1)
    bore = st.number_input("Bore (mm)", min_value=0, max_value=200, value=DEFAULTS["bore"], step=1)
    rod = st.number_input("Rod (mm)", min_value=0, max_value=200, value=DEFAULTS["rod"], step=1)

with col2:
    stroke = st.number_input("Stroke (mm)", min_value=0, max_value=2000, value=DEFAULTS["stroke"], step=5)
    closed_len = st.number_input("Closed Length (mm)", min_value=0, max_value=2500, value=DEFAULTS["closed_len"], step=5)
    application = st.selectbox("Application Type", APPLICATIONS, index=APPLICATIONS.index(DEFAULTS["application"]))
    cushion = st.selectbox("Cushioning Type", CUSHIONS, index=CUSHIONS.index(DEFAULTS["cushion"]))

# ---------- Dynamic calculation ----------
weight = (np.pi / 4) * (0.00000785) * (tube_OD**2 * closed_len - (bore**2 - rod**2) * stroke)

# ---------- Custom Font Size ----------
st.markdown("""
    <style>
    .stSlider label, .stSelectbox label {
        font-size: 22px !important;
        font-weight: 600;
    }
    h1 {
        font-size: 40px !important;
        font-weight: 800;
    }
    .css-184tjsw p {
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

if weight < 0:
    st.warning("Estimated weight is negative. Please check inputs.")

# ---------- Prediction ----------
input_df = pd.DataFrame([{
    "Est. Wt (Kg)": weight,
    "Rod": rod,
    "Stroke": stroke,
    "Tube_OD": tube_OD,
    "Application": application,
    "Cushion Type": cushion
}])

try:
    pred = model.predict(input_df)[0]

    st.markdown("Dynamic Results")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated Weight (Kg)", f"{weight:,.2f}")
    m2.metric("Predicted Cost (₹)", f"{pred:,.2f}")

    with st.expander("Show model input row"):
        st.dataframe(input_df)

except Exception as e:
    st.error("Prediction failed.")
    st.code(str(e))

