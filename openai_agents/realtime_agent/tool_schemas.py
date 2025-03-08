rt_tool_schemas_dict = {
    "get_coordinates": {
        "type": "function",  # <-- Add this
        "name": "get_coordinates",
        "description": "Get latitude and longitude for a given city name.",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city to get coordinates for."
                }
            },
            "required": ["city_name"]
        }
    },
    "get_current_weather": {
        "type": "function",  # <-- And here
        "name": "get_current_weather",
        "description": "Get current weather data for a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "The latitude of the location."
                },
                "lon": {
                    "type": "number",
                    "description": "The longitude of the location."
                }
            },
            "required": ["lat", "lon"]
        }
    }
}


test_dict = {
    "generate_horoscope": {
            "type": "function",
        "name": "generate_horoscope",
        "description": "Give today's horoscope for an astrological sign.",
        "parameters": {
          "type": "object",
          "properties": {
            "sign": {
              "type": "string",
              "description": "The sign for the horoscope.",
              "enum": [
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
                "Capricorn",
                "Aquarius",
                "Pisces"
              ]
            }
          },
          "required": ["sign"]
        }
      }
}