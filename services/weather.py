import requests

API_KEY = "2f9441196b423625b2c692cb25f2a702"

def get_weather(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    weather = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "rainfall": data.get("rain", {}).get("1h", 0),
        "wind_speed": data["wind"]["speed"],
        "city": data["name"]
    }

    return weather