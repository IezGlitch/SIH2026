from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS


# ============================================================
# APP SETUP
# ============================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# LOAD ML MODEL
# ============================================================

MODEL_PATH = BASE_DIR / "models" / "flood_risk_model.pkl"

model = joblib.load(MODEL_PATH)


# ============================================================
# LOAD REAL WEATHER DATA
# ============================================================

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "final_weather_flood_dataset.csv"
)

weather_df = pd.read_csv(DATA_PATH)

weather_df["datetime"] = pd.to_datetime(
    weather_df["datetime"],
    errors="coerce"
)


# ============================================================
# MODEL FEATURES
# ============================================================

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


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return send_file(
        BASE_DIR / "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": True,
        "weather_rows": len(weather_df)
    })


# ============================================================
# DISTRICTS API
# ============================================================

@app.route("/districts", methods=["GET"])
def districts():

    data = weather_df.copy()

    # Make district names consistent
    data["district_key"] = (
        data["district_key"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Get unique districts
    district_names = (
        data["district_key"]
        .dropna()
        .unique()
        .tolist()
    )

    # Convert into clean display names
    district_names = [
        district.strip().title()
        for district in district_names
    ]

    district_names.sort()

    return jsonify(district_names)


# ============================================================
# WEATHER API
# ============================================================

@app.route("/weather", methods=["GET"])
def weather():

    district = (
        request.args
        .get("district", "")
        .strip()
        .lower()
    )

    data = weather_df.copy()

    # --------------------------------------------------------
    # Make district key consistent
    # --------------------------------------------------------

    data["district_key"] = (
        data["district_key"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------------
    # Filter selected district
    # --------------------------------------------------------

    if district:

        data = data[
            data["district_key"] == district
        ].copy()

        # No matching district
        if data.empty:
            return jsonify([])

    # --------------------------------------------------------
    # Convert datetime
    # --------------------------------------------------------

    data["datetime"] = pd.to_datetime(
        data["datetime"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Latest record
    # --------------------------------------------------------

    if district:

        # Return latest record for selected district
        data = (
            data
            .sort_values(
                "datetime",
                ascending=False
            )
            .head(1)
        )

    else:

        # Return latest record for EVERY district
        data = (
            data
            .sort_values(
                "datetime",
                ascending=False
            )
            .groupby(
                "district_key",
                as_index=False
            )
            .head(1)
        )

    # --------------------------------------------------------
    # Replace NaN with None
    # --------------------------------------------------------

    data = data.astype(object).where(
        pd.notna(data),
        None
    )

    # --------------------------------------------------------
    # Return JSON
    # --------------------------------------------------------

    return jsonify(
        data.to_dict(
            orient="records"
        )
    )


# ============================================================
# FLOOD PREDICTION API
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No input data received"
        }), 400

    # --------------------------------------------------------
    # Check missing features
    # --------------------------------------------------------

    missing = [
        feature
        for feature in FEATURES
        if feature not in data
    ]

    if missing:

        return jsonify({
            "error": "Missing required features",
            "missing": missing
        }), 400

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    try:

        input_data = pd.DataFrame(
            [[
                data[feature]
                for feature in FEATURES
            ]],
            columns=FEATURES
        )

        prediction = model.predict(
            input_data
        )[0]

        result = {
            "prediction": int(prediction)
        }

        # ----------------------------------------------------
        # Prediction probability
        # ----------------------------------------------------

        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = model.predict_proba(
                input_data
            )[0]

            result["probability"] = float(
                max(probabilities)
            )

        # ----------------------------------------------------
        # Risk level
        # ----------------------------------------------------

        if int(prediction) == 1:

            result["risk_level"] = "HIGH"

        else:

            result["risk_level"] = "LOW"

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )