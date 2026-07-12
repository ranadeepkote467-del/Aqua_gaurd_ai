from flask import Flask, render_template, request
import joblib
import numpy as np
from services.weather import get_weather
app = Flask(__name__)

# Load trained model
model = joblib.load("models/flood_model.pkl")


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/weather", methods=["POST"])
def weather():

    lat = request.form["lat"]
    lon = request.form["lon"]

    weather = get_weather(lat, lon)

    return weather
@app.route("/predict", methods=["POST"])
def predict():

    # Get values from form
    rainfall = float(request.form["rainfall"])
    river_level = float(request.form["river_level"])
    humidity = float(request.form["humidity"])
    temperature = float(request.form["temperature"])
    soil_moisture = float(request.form["soil_moisture"])
    elevation = float(request.form["elevation"])

    # Convert percentages to decimals if your model was trained that way
    drainage = float(request.form["drainage"]) / 100
    urbanization = float(request.form["urbanization"]) / 100

    # Prepare data for prediction
    data = np.array([[
        rainfall,
        river_level,
        humidity,
        temperature,
        soil_moisture,
        elevation,
        drainage,
        urbanization
    ]])

    # Predict class
    prediction = model.predict(data)

    # Default values
    confidence = None

    if prediction[0] == 1:
        result = "⚠ HIGH FLOOD RISK"
        risk_score = 100
    else:
        result = "✅ NO FLOOD RISK"
        risk_score = 0

    # If model supports probabilities
    try:
        probability = model.predict_proba(data)

        confidence = round(
            float(max(probability[0])) * 100,
            2
        )

        risk_score = round(
            float(probability[0][1]) * 100,
            2
        )

    except:
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


if __name__ == "__main__":
    app.run(debug=True)