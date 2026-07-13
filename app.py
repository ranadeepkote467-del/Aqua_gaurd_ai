import os
import re
from io import BytesIO

from flask import (
    Flask, render_template, request, jsonify,
    send_file, session, redirect, url_for, make_response
)
from flask_cors import CORS
from dotenv import load_dotenv
import joblib
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

load_dotenv()

from services.weather import get_weather

app = Flask(__name__)

# Secret key for session cookies (change this in production)
app.secret_key = os.getenv("SECRET_KEY", "aquaguard-ai-secret-2026")

# Allow browser requests (restrict via CORS_ORIGINS env var, comma-separated).
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins.strip() == "*":
    CORS(app)  # Allow all origins
else:
    origin_list = [o.strip() for o in cors_origins.split(",") if o.strip()]
    CORS(app, resources={r"/*": {"origins": origin_list}})

# Load trained model
model = joblib.load("models/flood_model.pkl")


# =====================================
# HOME PAGE
# =====================================
@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# HEALTH CHECK (keep Render instance warm)
# =====================================
@app.route("/ping")
@app.route("/health")
def ping():
    return jsonify({"status": "ok", "service": "AquaGuard AI"}), 200


# =====================================
# WEATHER API
# =====================================
@app.route("/weather", methods=["POST"])
def weather():

    try:

        data = request.get_json(force=True)

        if not data or "lat" not in data or "lon" not in data:
            return jsonify({"error": "Missing lat/lon in request body"}), 400

        lat = data["lat"]
        lon = data["lon"]

        weather_data = get_weather(lat, lon)

        # get_weather always returns a dict (never None) – demo fallback is built in
        return jsonify(weather_data)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =====================================
# FLOOD PREDICTION
# =====================================
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

        # Save latest report in session (persists across server restarts)
        session["latest_report"] = {

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
        # Explicitly mark session as modified so Flask sends the Set-Cookie header
        session.modified = True

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


def _safe(text):
    """Strip characters outside Latin-1 range so ReportLab Helvetica won't crash."""
    if text is None:
        return "N/A"
    return re.sub(r'[^\x00-\xff]', '', str(text)).strip()


@app.route("/download-report")
def download_report():

    report = session.get("latest_report")

    if not report:
        # No prediction yet — send user back to home with a message
        return redirect(url_for("home") + "?msg=no_report")

    try:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        y = 800

        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(170, y, "AquaGuard AI")

        y -= 35

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(130, y, "Flood Prediction Report")

        y -= 45

        pdf.setFont("Helvetica", 12)

        pdf.drawString(50, y, f"Prediction : {_safe(report['prediction'])}")
        y -= 25

        pdf.drawString(50, y, f"Confidence : {report['confidence']} %")
        y -= 25

        pdf.drawString(50, y, f"Flood Risk  : {report['risk_score']} %")

        y -= 40

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "Environmental Inputs")

        y -= 25

        pdf.setFont("Helvetica", 12)

        pdf.drawString(60, y, f"Temperature     : {report['temperature']} deg C")
        y -= 20

        pdf.drawString(60, y, f"Humidity        : {report['humidity']} %")
        y -= 20

        pdf.drawString(60, y, f"Rainfall        : {report['rainfall']} mm")
        y -= 20

        pdf.drawString(60, y, f"River Level     : {report['river_level']} m")
        y -= 20

        pdf.drawString(60, y, f"Soil Moisture   : {report['soil_moisture']} %")
        y -= 20

        pdf.drawString(60, y, f"Elevation       : {report['elevation']} m")
        y -= 20

        pdf.drawString(60, y, f"Drainage Capacity: {report['drainage']} %")
        y -= 20

        pdf.drawString(60, y, f"Urbanization    : {report['urbanization']} %")

        y -= 40

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "AI Analysis")

        y -= 25

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(60, y, _safe(report["ai_title"]))

        y -= 25

        text = pdf.beginText(60, y)
        text.setFont("Helvetica", 11)
        text.textLines(_safe(report["ai_message"]))
        pdf.drawText(text)

        pdf.save()
        pdf_bytes = buffer.getvalue()

        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = 'attachment; filename="Flood_Report.pdf"'
        response.headers["Content-Length"] = str(len(pdf_bytes))
        return response

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


# =====================================
# RUN APPLICATION
# =====================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )