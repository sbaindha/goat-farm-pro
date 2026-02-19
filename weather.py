import os
import requests
from dotenv import load_dotenv

load_dotenv()  # .env file se API key load karta hai

API_KEY    = os.environ.get("WEATHER_API_KEY")
DEFAULT_LAT = 26.9124
DEFAULT_LNG = 75.7873
BASE_URL   = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

def get_weather(lat=DEFAULT_LAT, lng=DEFAULT_LNG):
    if not API_KEY:
        raise ValueError("WEATHER_API_KEY .env file mein nahi mili!")

    url = f"{BASE_URL}{lat},{lng}?unitGroup=metric&key={API_KEY}&contentType=json"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    current = data["currentConditions"]
    print(f"📍 Location : {data['resolvedAddress']}")
    print(f"🌡️  Temp     : {current['temp']}°C")
    print(f"🌤️  Condition: {current['conditions']}")
    print(f"💧 Humidity : {current['humidity']}%")
    print(f"💨 Wind     : {current['windspeed']} km/h")

if __name__ == "__main__":
    get_weather()
