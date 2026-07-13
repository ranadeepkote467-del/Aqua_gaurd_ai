import os

import requests

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


def get_weather(lat, lon):
    if not API_KEY:
        return None

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0),
            "wind_speed": data["wind"]["speed"],
            "city": data["name"],
        }

        return weather

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None