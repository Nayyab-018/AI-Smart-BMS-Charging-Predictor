# 🔋 AI Smart Battery Management System (BMS) & Charging Predictor

### 🌐 [Launch Live Interactive BMS & ML Predictor App →](https://ai-smart-bms-charging-predictor-ixudssaqt27j42yvsxsudw.streamlit.app/)
### 📸 Live Application Preview
![AI Smart BMS & Charging Predictor Dashboard](bms_dashboard.png)


An end-to-end **Embedded Hardware + Machine Learning** system designed to simulate intelligent Li-Ion battery charging, thermal throttling protection, and real-time time-to-full prediction for a 5000mAh smartphone battery.

---

### 🚀 Key Engineering Features

* **Embedded BMS Controller (`firmware/smart_bms_controller.ino`):**
  * Implements **CC-CV (Constant Current – Constant Voltage)** charging stages (fast charging below 80%, trickle charging from 80%–99%, and full cutoff at 100%).
  * Uses a **10kΩ NTC Thermistor (Steinhart-Hart equation)** to trigger automatic **thermal throttling** and audio-visual alerts whenever cell temperature exceeds `42.0°C`.
  * Streams structured CSV telemetry (`Battery_Pct, Voltage_V, Temp_C, Current_A, Charging_Mode, Est_Mins_Left`) over Serial.
* **Machine Learning Charging Predictor (`app.py`):**
  * Trains a **Random Forest Regressor** (`scikit-learn`) on 4,000 physics-informed charging cycles across `15W`, `25W`, and `45W` adapters.
  * Predicts exact **Minutes to 100%** and plots a dynamic **Current % → 100% charging curve** in an interactive **Streamlit** dashboard.

---

### 🛠 Tech Stack & Project Structure

* **Hardware & Firmware:** C++ (Arduino Uno), 10kΩ NTC Thermistor, Potentiometer, Piezo Buzzer
* **Machine Learning & UI:** Python, `scikit-learn`, `NumPy`, `Pandas`, `Streamlit`

```text
AI-Smart-BMS-Charging-Predictor/
├── firmware/
│   └── smart_bms_controller.ino   # Embedded C++ CC-CV & thermal protection logic
├── app.py                         # Random Forest ML model & Streamlit web dashboard
├── requirements.txt               # Python dependencies for Streamlit Cloud deployment
└── README.md
```

---

### 💻 Run Locally

```bash
git clone https://github.com
cd AI-Smart-BMS-Charging-Predictor
pip install -r requirements.txt
streamlit run app.py
```
