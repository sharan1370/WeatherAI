import requests
from datetime import date, timedelta

from crewai.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _get_location(location: str):
    """Convert city name to latitude/longitude."""

    geo_params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        response = requests.get(
            GEOCODING_URL,
            params=geo_params,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        return None, f"Location service error: {e}"

    results = data.get("results")

    if not results:
        return None, f"Location '{location}' could not be found."

    place = results[0]

    return place, None


@tool("Weather Forecast Tool")
def get_weather_forecast(
    location: str,
    forecast_days: int = 1,
) -> str:
    """
    Get future weather forecast.

    forecast_days:
        1 = tomorrow
        3 = next 3 days
        7 = next 7 days
    """

    # --------------------------------------------------
    # Validate forecast days
    # --------------------------------------------------

    try:
        forecast_days = int(forecast_days)
    except (ValueError, TypeError):
        forecast_days = 1

    forecast_days = max(1, min(forecast_days, 16))

    # --------------------------------------------------
    # GEOCODING
    # --------------------------------------------------

    place, error = _get_location(location)

    if error:
        return error

    latitude = place["latitude"]
    longitude = place["longitude"]

    city = place["name"]
    country = place.get("country", "")
    timezone = place.get("timezone", "")

    # --------------------------------------------------
    # FORECAST API
    # --------------------------------------------------

    forecast_params = {
        "latitude": latitude,
        "longitude": longitude,

        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "uv_index_max",
            "sunrise",
            "sunset",
        ],

        "forecast_days": forecast_days + 1,
        "timezone": "auto",
    }

    try:
        response = requests.get(
            FORECAST_URL,
            params=forecast_params,
            timeout=20,
        )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        return f"Forecast service error: {e}"

    daily = data.get("daily", {})

    dates = daily.get("time", [])

    if len(dates) <= 1:
        return "No future forecast data was returned."

    # --------------------------------------------------
    # FORMAT
    # --------------------------------------------------

    output = []

    output.append("WEATHER FORECAST")
    output.append(f"Location: {city}, {country}")
    output.append(f"Coordinates: {latitude}, {longitude}")
    output.append(f"Timezone: {timezone}")
    output.append("")

    # Skip today
    for i in range(1, len(dates)):

        output.append(f"DATE: {dates[i]}")

        output.append(
            f"Weather Code: "
            f"{daily['weather_code'][i]}"
        )

        output.append(
            f"Maximum Temperature: "
            f"{daily['temperature_2m_max'][i]} °C"
        )

        output.append(
            f"Minimum Temperature: "
            f"{daily['temperature_2m_min'][i]} °C"
        )

        output.append(
            f"Maximum Feels Like: "
            f"{daily['apparent_temperature_max'][i]} °C"
        )

        output.append(
            f"Minimum Feels Like: "
            f"{daily['apparent_temperature_min'][i]} °C"
        )

        output.append(
            f"Precipitation: "
            f"{daily['precipitation_sum'][i]} mm"
        )

        output.append(
            f"Rain: "
            f"{daily['rain_sum'][i]} mm"
        )

        output.append(
            f"Rain Probability: "
            f"{daily['precipitation_probability_max'][i]} %"
        )

        output.append(
            f"Maximum Wind: "
            f"{daily['wind_speed_10m_max'][i]} km/h"
        )

        output.append(
            f"Maximum Wind Gusts: "
            f"{daily['wind_gusts_10m_max'][i]} km/h"
        )

        output.append(
            f"Maximum UV Index: "
            f"{daily['uv_index_max'][i]}"
        )

        output.append(
            f"Sunrise: "
            f"{daily['sunrise'][i]}"
        )

        output.append(
            f"Sunset: "
            f"{daily['sunset'][i]}"
        )

        output.append("")

    output.append(
        "DATA SOURCE: Open-Meteo Forecast API"
    )

    return "\n".join(output)