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

    response = requests.get(url, timeout=10)

        return None

    except Exception as e:

        print(f"Unexpected Error: {e}")

        return None