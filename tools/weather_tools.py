import requests

from crewai.tools import tool


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


@tool("Current Weather Tool")
def get_current_weather(location: str) -> str:
    """
    Get current weather for a city using Open-Meteo.
    """

    # --------------------------------------------------
    # 1. Convert city name to coordinates
    # --------------------------------------------------

    geocoding_params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        geo_response = requests.get(
            GEOCODING_URL,
            params=geocoding_params,
            timeout=20,
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

    except requests.RequestException as e:
        return f"Location service error: {e}"

    results = geo_data.get("results")

    if not results:
        return (
            f"Location '{location}' "
            "could not be found."
        )

    place = results[0]

    latitude = place["latitude"]
    longitude = place["longitude"]

    city_name = place["name"]

    country = place.get(
        "country",
        ""
    )

    timezone = place.get(
        "timezone",
        ""
    )

    # --------------------------------------------------
    # 2. Get current weather
    # --------------------------------------------------

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation",
            "rain",
            "showers",
            "cloud_cover",
            "visibility",
            "pressure_msl",
            "surface_pressure",
            "dew_point_2m",
            "uv_index",
            "is_day",
        ],

        "timezone": "auto",
    }

    try:
        weather_response = requests.get(
            WEATHER_URL,
            params=weather_params,
            timeout=20,
        )
        
        weather_response.raise_for_status()

        weather_data = (
            weather_response.json()
        )
        print(weather_data)
    except requests.RequestException as e:
        return (
            f"Weather service error: {e}"
        )

    current = weather_data.get(
        "current",
        {}
    )

    # --------------------------------------------------
    # 3. Format result
    # --------------------------------------------------

    result = f"""
CURRENT WEATHER

Location:
{city_name}, {country}

Coordinates:
Latitude: {latitude}
Longitude: {longitude}

Timezone:
{timezone}

Observation Time:
{current.get("time")}

Temperature:
{current.get("temperature_2m")} °C

Feels Like:
{current.get("apparent_temperature")} °C

Humidity:
{current.get("relative_humidity_2m")} %

Dew Point:
{current.get("dew_point_2m")} °C

Wind Speed:
{current.get("wind_speed_10m")} km/h

Wind Direction:
{current.get("wind_direction_10m")}°

Wind Gusts:
{current.get("wind_gusts_10m")} km/h

Precipitation:
{current.get("precipitation")} mm

Rain:
{current.get("rain")} mm

Showers:
{current.get("showers")} mm

Cloud Cover:
{current.get("cloud_cover")} %

Visibility:
{current.get("visibility")} m

Pressure:
{current.get("pressure_msl")} hPa

Surface Pressure:
{current.get("surface_pressure")} hPa

UV Index:
{current.get("uv_index")}

Weather Code:
{current.get("weather_code")}

Is Day:
{current.get("is_day")}

DATA SOURCE:
Open-Meteo
"""

    return result.strip()