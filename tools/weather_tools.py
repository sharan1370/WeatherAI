import requests
import time

from crewai.tools import tool


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

CURRENT_CACHE_TTL_SECONDS = 300
_current_weather_cache = {}
OPEN_METEO_HEADERS = {
    "User-Agent": "WeatherAI/1.0 (weather assistant)",
}


@tool("Current Weather Tool")
def get_current_weather(location: str) -> str:
    """
    Get current weather for a city using Open-Meteo.
    """

    cache_key = location.strip().lower()
    cached_result = _current_weather_cache.get(cache_key)

    if cached_result and time.monotonic() - cached_result[0] < CURRENT_CACHE_TTL_SECONDS:
        return cached_result[1]

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
            headers=OPEN_METEO_HEADERS,
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
            headers=OPEN_METEO_HEADERS,
        )

        if weather_response.status_code == 429:
            return (
                "Open-Meteo is temporarily rate-limiting requests from the "
                "deployment server. Please wait a few minutes and try again."
            )
        
        weather_response.raise_for_status()

        weather_data = (
            weather_response.json()
        )
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

    result = result.strip()
    _current_weather_cache[cache_key] = (time.monotonic(), result)

    return result
