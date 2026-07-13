import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


def _demo_weather(lat, lon):
    latitude = float(lat)
    longitude = float(lon)

    temperature = round(24 + (latitude % 7) - (longitude % 5), 1)
    humidity = int(55 + abs(latitude + longitude) % 30)
    rainfall = round(abs(latitude * longitude) % 12, 1)
    wind_speed = round(2 + abs(latitude - longitude) % 6, 1)

    return {
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall,
        "wind_speed": wind_speed,
        "city": "Demo Location",
        "demo": True,
    }


def get_weather(lat, lon):
    if not API_KEY:
        print("No API key found, using demo weather data.")
        return _demo_weather(lat, lon)

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(
                f"OpenWeather request failed: HTTP {response.status_code} – "
                f"{response.text[:200]}"
            )
            print("Falling back to demo weather data.")
            return _demo_weather(lat, lon)

        data = response.json()

        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0),
            "wind_speed": data["wind"]["speed"],
            "city": data["name"],
            "demo": False,
        }

        return weather

    except Exception as e:
        print(f"Unexpected weather fetch error: {e}")
        print("Falling back to demo weather data.")
        return _demo_weather(lat, lon)