tool_schemas_dict = {
    "get_coordinates": {
        "type": "function",
        "function": {
            "name": "get_coordinates",
            "description": "Get latitude and longitude for a given city name using the OpenWeatherMap Geocoding API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "The name of the city to get coordinates for, e.g., 'New York'."
                    }
                },
                "required": ["city_name"],
                "additionalProperties": False  # Disallow additional fields
            },
            "strict": True  # Enforce schema adherence
        }
    },
    "get_current_weather": {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather data for a specific location identified by latitude and longitude.",
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
                "required": ["lat", "lon"],
                "additionalProperties": False  # Disallow additional fields
            },
            "strict": True  # Enforce schema adherence
        }
    }
}
