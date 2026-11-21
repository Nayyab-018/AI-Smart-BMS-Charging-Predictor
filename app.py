import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

st.set_page_config(page_title="AI Smart BMS & Charging Predictor", page_icon="🔋", layout="centered")

@st.cache_resource
def train_bms_model():
    np.random.seed(42)
    n_samples = 4000
    battery_pct = np.random.randint(1, 100, n_samples)
    charger_wattage = np.random.choice([15, 25, 45], n_samples)
    temp_c = np.random.uniform(20.0, 50.0, n_samples)
    battery_health_pct = np.random.uniform(80.0, 100.0, n_samples)

    # Physics-informed Li-Ion CC-CV charging simulation (5000mAh cell)
    effective_capacity_ah = 5.0 * (battery_health_pct / 100.0)
    remaining_ah = effective_capacity_ah * ((100.0 - battery_pct) / 100.0)
    base_current = (charger_wattage / 3.8) * 0.85

    # Constant Voltage (CV) slowdown >= 80% and Thermal Throttling >= 42°C
    cv_factor = np.where(battery_pct >= 80, 0.45, 1.0)
    thermal_factor = np.where(temp_c >= 42.0, 0.35, np.where(temp_c >= 38.0, 0.70, 1.0))

    actual_current = base_current * cv_factor * thermal_factor
    minutes_to_full = np.clip((remaining_ah / actual_current) * 60.0 + np.random.normal(0, 1.2, n_samples), 1, 300)

    X = np.column_stack([battery_pct, charger_wattage, temp_c, battery_health_pct])
    X_train, X_test, y_train, y_test = train_test_split(X, minutes_to_full, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=120, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {"r2": r2_score(y_test, preds), "mae": mean_absolute_error(y_test, preds)}
    return model, metrics

model, metrics = train_bms_model()

st.title("🔋 AI Smart Battery Management & Charging Predictor")
st.markdown("End-to-end **Embedded BMS + Machine Learning** system predicting Li-Ion remaining charge time, CC-CV charging stages, and thermal throttling protection.")

st.sidebar.header("⚡ Live Sensor & Charger Inputs")
battery_pct = st.sidebar.slider("Current Battery Level (%)", 1, 99, 35)
charger_wattage = st.sidebar.selectbox("Charger Adapter Power (W)", [15, 25, 45], index=1)
temp_c = st.sidebar.slider("Battery Temperature (°C)", 20.0, 50.0, 32.0, 0.5)
battery_health = st.sidebar.slider("Battery State of Health (%)", 80, 100, 96)

est_minutes = model.predict(np.array([[battery_pct, charger_wattage, temp_c, battery_health]]))[0]
est_voltage = 3.20 + (battery_pct / 100.0) * 1.00

if temp_c >= 42.0:
    status = "🚨 THERMAL THROTTLING ACTIVE — Current capped to prevent Li-Ion degradation"
elif battery_pct >= 80:
    status = "🛡️ TRICKLE CHARGING (Constant Voltage Stage — 80% to 100%)"
else:
    status = f"⚡ FAST CHARGING ACTIVE ({charger_wattage}W Constant Current Stage)"

st.subheader("📊 Real-Time BMS Telemetry & ML Prediction")
col1, col2, col3 = st.columns(3)
col1.metric("Est. Time to 100%", f"{int(round(est_minutes))} mins")
col2.metric("Battery Temperature", f"{temp_c:.1f} °C", delta="Overheat Risk" if temp_c >= 42 else "Optimal", delta_color="inverse")
col3.metric("Cell Voltage", f"{est_voltage:.2f} V")

st.info(f"**BMS Controller Mode:** {status}")

st.subheader("📈 Predicted Charging Curve (Current % → 100%)")
pct_range = np.arange(battery_pct, 100)
curve_inputs = np.column_stack([
    pct_range,
    np.full_like(pct_range, charger_wattage),
    np.full_like(pct_range, temp_c),
    np.full_like(pct_range, battery_health)
])
remaining_times = model.predict(curve_inputs)
elapsed_times = est_minutes - remaining_times

chart_df = pd.DataFrame({"Battery Percentage (%)": pct_range}, index=np.round(elapsed_times, 1))
st.line_chart(chart_df)

with st.expander("🧠 Model Architecture & Validation Metrics"):
    st.write(f"**Algorithm:** Random Forest Regressor (`n_estimators=120`) trained on 4,000 physics-informed 5000mAh Li-Ion charging cycles.")
    st.write(f"**Test Set R² Accuracy:** `{metrics['r2']:.4f}` | **Mean Absolute Error (MAE):** `{metrics['mae']:.2f} mins`")
