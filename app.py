from flask import Flask, render_template, request, jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import joblib
import numpy as np

from services.weather import get_weather

app = Flask(__name__)

# Store latest prediction
latest_report = {}

# Load ML Model
model = joblib.load("models/flood_model.pkl")


# =====================================
# HOME PAGE
# =====================================
@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# WEATHER API
# =====================================
@app.route("/weather", methods=["POST"])
def weather():

    try:

        data = request.get_json()

        lat = data["lat"]
        lon = data["lon"]

        weather = get_weather(lat, lon)

        if weather is None:
            return jsonify({"error": "Unable to fetch weather"}), 500

        return jsonify(weather)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =====================================
# FLOOD PREDICTION
# =====================================
@app.route("/predict", methods=["POST"])
def predict():

    global latest_report

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

            ai_title = "⚠ High Flood Risk Detected"

            ai_message = (
                "The AI predicts a HIGH probability of flooding based on "
                "rainfall, river level and environmental conditions. "
                "Residents should avoid rivers, prepare emergency kits "
                "and follow government alerts."
            )

        else:

            result = "✅ NO FLOOD RISK"

            risk_score = 0

            ai_title = "✅ Area Appears Safe"

            ai_message = (
                "Current environmental conditions indicate a LOW probability "
                "of flooding. Weather is stable and there is no immediate "
                "threat. Continue monitoring weather updates."
            )

        try:

            probability = model.predict_proba(sample)

            confidence = round(
                float(max(probability[0])) * 100,
                2
            )

            risk_score = round(
                float(probability[0][1]) * 100,
                2
            )

        except Exception:
            confidence = None

        # Save latest report
        latest_report = {

            "prediction": result,
            "confidence": confidence,
            "risk_score": risk_score,

            "temperature": temperature,
            "humidity": humidity,
            "rainfall": rainfall,
            "river_level": river_level,
            "soil_moisture": soil_moisture,
            "elevation": elevation,

            "drainage": drainage * 100,
            "urbanization": urbanization * 100,

            "ai_title": ai_title,
            "ai_message": ai_message

        }

        return render_template(

            "result.html",

            prediction=result,

            confidence=confidence,

            risk_score=risk_score,

            ai_title=ai_title,

            ai_message=ai_message,

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

        return f"""
        <h2>Prediction Error</h2>
        <pre>{e}</pre>
        """


# =====================================
# DOWNLOAD PDF REPORT
# =====================================
@app.route("/download-report")
def download_report():

    pdf = canvas.Canvas("Flood_Report.pdf", pagesize=A4)

    y = 800

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(170, y, "AquaGuard AI")

    y -= 35

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(150, y, "Flood Prediction Report")

    y -= 45

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, y, f"Prediction : {latest_report['prediction']}")
    y -= 25

    pdf.drawString(50, y, f"Confidence : {latest_report['confidence']} %")
    y -= 25

    pdf.drawString(50, y, f"Flood Risk : {latest_report['risk_score']} %")

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Weather Information")

    y -= 25

    pdf.setFont("Helvetica", 12)

    pdf.drawString(60, y, f"Temperature : {latest_report['temperature']} °C")
    y -= 20

    pdf.drawString(60, y, f"Humidity : {latest_report['humidity']} %")
    y -= 20

    pdf.drawString(60, y, f"Rainfall : {latest_report['rainfall']} mm")
    y -= 20

    pdf.drawString(60, y, f"River Level : {latest_report['river_level']} m")
    y -= 20

    pdf.drawString(60, y, f"Soil Moisture : {latest_report['soil_moisture']} %")
    y -= 20

    pdf.drawString(60, y, f"Elevation : {latest_report['elevation']} m")
    y -= 20

    pdf.drawString(60, y, f"Drainage Capacity : {latest_report['drainage']} %")
    y -= 20

    pdf.drawString(60, y, f"Urbanization : {latest_report['urbanization']} %")

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "AI Analysis")

    y -= 25

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y, latest_report["ai_title"])

    y -= 25

    text = pdf.beginText(60, y)
    text.setFont("Helvetica", 11)
    text.textLines(latest_report["ai_message"])
    pdf.drawText(text)

    pdf.save()

    return send_file(
        "Flood_Report.pdf",
        as_attachment=True
    )


# =====================================
# RUN APPLICATION
# =====================================
if __name__ == "__main__":
    app.run(debug=True)