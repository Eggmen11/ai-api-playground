import os
import requests

def get_coordinates(city_name: str):
    """
    Return (lat, lon) for a given city name using the OpenWeatherMap Geocoding API.
    """
    api_key = os.environ["OPENWEATHER_API_KEY"]  # Make sure this is set in your environment or .env
    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "limit": 1,  # return only the first/best match
        "appid": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    if not data:
        raise ValueError(f"No matching coordinates found for city: {city_name}")

    lat = data[0]["lat"]
    lon = data[0]["lon"]
    return lat, lon

def get_current_weather(lat: float, lon: float):
    """
    Return current weather JSON for a given (lat, lon) 
    from the OpenWeatherMap 'Current Weather' endpoint.
    """
    api_key = os.environ["OPENWEATHER_API_KEY"]
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"  # change to 'imperial' if you want Fahrenheit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

# This dictionary maps names you'd use in your 'tool_schemas' or agent logic
# to the actual Python functions so you can call them dynamically.
tool_map = {
    "get_coordinates": get_coordinates,
    "get_current_weather": get_current_weather
}
