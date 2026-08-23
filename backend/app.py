from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request,send_file
from flask_cors import CORS


# --------------------------------------------------
# App setup
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Load trained ML model
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "flood_risk_model.pkl"

model = joblib.load(MODEL_PATH)
@app.route("/", methods=["GET"])
def home():
    return send_file(BASE_DIR / "index.html")



# These MUST match the features used while training
FEATURES = [
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "temperature_6h_avg",
    "humidity_6h_avg",
    "heat_risk",
    "rainfall_risk",
    "rainfall_intensity",
    "humidity_rain_index",
    "flood_pressure_index",
    "hour",
    "day",
    "month",
]


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": True
    })


# --------------------------------------------------
# Prediction API
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No input data received"
        }), 400

    # Check for missing features
    missing = [feature for feature in FEATURES if feature not in data]

    if missing:
        return jsonify({
            "error": "Missing required features",
            "missing": missing
        }), 400

    try:
        # Keep feature order exactly the same as training
        input_data = pd.DataFrame(
            [[data[feature] for feature in FEATURES]],
            columns=FEATURES
        )

        prediction = model.predict(input_data)[0]

        result = {
            "prediction": int(prediction)
        }

        # Probability if the model supports it
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_data)[0]
            result["probability"] = float(max(probabilities))

        # Convert model output into dashboard-friendly risk
        if int(prediction) == 1:
            result["risk_level"] = "HIGH"
        else:
            result["risk_level"] = "LOW"

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------
# Run server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )