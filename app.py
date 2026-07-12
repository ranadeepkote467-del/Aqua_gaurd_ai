from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

from services.weather import get_weather

app = Flask(__name__)

# Load trained model
model = joblib.load("models/flood_model.pkl")


# ==========================
# Home Page
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# Weather API
# ==========================
@app.route("/weather", methods=["POST"])
def weather():

    try:
        data = request.get_json()

        lat = data["lat"]
        lon = data["lon"]

        weather_data = get_weather(lat, lon)

        if weather_data is None:
            return jsonify({
                "error": "Unable to fetch weather."
            }), 500

        return jsonify(weather_data)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==========================
# Flood Prediction
# ==========================
@app.route("/predict", methods=["POST"])
def predict():

    try:

        rainfall = float(request.form["rainfall"])
        river_level = float(request.form["river_level"])
        humidity = float(request.form["humidity"])
        temperature = float(request.form["temperature"])
        soil_moisture = float(request.form["soil_moisture"])
        elevation = float(request.form["elevation"])

        drainage = float(request.form["drainage"]) / 100
        urbanization = float(request.form["urbanization"]) / 100

        sample = np.array([[
            rainfall,
            river_level,
            humidity,
            temperature,
            soil_moisture,
            elevation,
            drainage,
            urbanization
        ]])

        prediction = model.predict(sample)

        confidence = None

        if prediction[0] == 1:
            result = "⚠ HIGH FLOOD RISK"
            risk_score = 100
        else:
            result = "✅ NO FLOOD RISK"
            risk_score = 0

        try:

            probabilities = model.predict_proba(sample)

            confidence = round(
                float(max(probabilities[0])) * 100,
                2
            )

            risk_score = round(
                float(probabilities[0][1]) * 100,
                2
            )

        except Exception:
            pass

        return render_template(
            "result.html",

            prediction=result,
            confidence=confidence,
            risk_score=risk_score,

            rainfall=rainfall,
            river_level=river_level,
            humidity=humidity,
            temperature=temperature,
            soil_moisture=soil_moisture,
            elevation=elevation,

            drainage=drainage * 100,
            urbanization=urbanization * 100
        )

    except Exception as e:

        return f"<h2>Error</h2><pre>{e}</pre>"


# ==========================
# Run Server
# ==========================
if __name__ == "__main__":
    app.run(debug=True)