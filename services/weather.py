import requests

API_KEY = "2f9441196b423625b2c692cb25f2a702"


def get_weather(lat, lon):

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    try:

        response = requests.get(url, timeout=10)

        response.raise_for_status()

        data = response.json()

        weather = {

            "temperature": int(round(data["main"]["temp"])),

            "humidity": int(round(data["main"]["humidity"])),

            "rainfall": round(
                data.get("rain", {}).get("1h", 0),
                1
            ),

            "wind_speed": round(
                data["wind"]["speed"],
                1
            ),

            "city": data.get("name", "Unknown")

        }

        return weather

    except requests.exceptions.RequestException as e:

        print(f"Weather API Error: {e}")

        return None

    except Exception as e:

        print(f"Unexpected Error: {e}")

        return None