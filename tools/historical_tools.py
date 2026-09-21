import requests
from datetime import date, timedelta, datetime

from crewai.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/era5"


def _get_location(location: str):
    """Convert city name to coordinates."""

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

    return results[0], None


@tool("Historical Weather Tool")
def get_historical_weather(
    location: str,
    start_date: str,
    end_date: str,
) -> str:
    """
    Get historical weather.

    For recent dates within the last 10 days,
    use the Open-Meteo forecast API with past_days.

    For older dates, use the Open-Meteo ERA5 archive API.
    """

    # --------------------------------------------------
    # VALIDATE DATES
    # --------------------------------------------------

    try:
        start = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        ).date()

        end = datetime.strptime(
            end_date,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        return (
            "Invalid date format. "
            "Use YYYY-MM-DD."
        )

    if start > end:
        return (
            "Start date cannot be after "
            "end date."
        )

    today = date.today()

    if end > today:
        return (
            "Historical data cannot be requested "
            "for a future date."
        )

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
    # DETERMINE WHICH API TO USE
    # --------------------------------------------------

    days_old = (today - start).days

    is_recent = (
        days_old <= 10
        and (today - end).days <= 10
    )

    # ==================================================
    # RECENT PAST WEATHER
    # Open-Meteo Forecast API + past_days
    # ==================================================

    if is_recent:

        past_days = (today - start).days + 1

        past_days = max(1, min(past_days, 10))

        params = {
            "latitude": latitude,
            "longitude": longitude,

            "past_days": past_days,

            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "showers",
                "weather_code",
                "wind_speed_10m",
                "wind_gusts_10m",
                "cloud_cover",
                "pressure_msl",
                "visibility",
                "uv_index",
            ],

            "timezone": "auto",
        }

        try:
            response = requests.get(
                FORECAST_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as e:
            return (
                f"Recent weather service error: {e}"
            )

        hourly = data.get("hourly", {})

        times = hourly.get("time", [])

        if not times:
            return (
                "No recent historical weather "
                "data was returned."
            )

        output = []

        output.append(
            "RECENT HISTORICAL WEATHER"
        )

        output.append(
            f"Location: {city}, {country}"
        )

        output.append(
            f"Coordinates: "
            f"{latitude}, {longitude}"
        )

        output.append(
            f"Timezone: {timezone}"
        )

        output.append(
            f"Requested Period: "
            f"{start_date} to {end_date}"
        )

        output.append("")

        # --------------------------------------------------
        # Group hourly data by requested date
        # --------------------------------------------------

        requested_dates = []

        current_date = start

        while current_date <= end:
            requested_dates.append(
                current_date.isoformat()
            )
            current_date += timedelta(days=1)

        for requested_date in requested_dates:

            indexes = [
                i
                for i, timestamp in enumerate(times)
                if timestamp.startswith(requested_date)
            ]

            if not indexes:
                continue

            temperatures = [
                hourly["temperature_2m"][i]
                for i in indexes
                if hourly.get("temperature_2m")
                and hourly["temperature_2m"][i] is not None
            ]

            humidity = [
                hourly["relative_humidity_2m"][i]
                for i in indexes
                if hourly.get("relative_humidity_2m")
                and hourly["relative_humidity_2m"][i] is not None
            ]

            precipitation = [
                hourly["precipitation"][i]
                for i in indexes
                if hourly.get("precipitation")
                and hourly["precipitation"][i] is not None
            ]

            rain = [
                hourly["rain"][i]
                for i in indexes
                if hourly.get("rain")
                and hourly["rain"][i] is not None
            ]

            wind = [
                hourly["wind_speed_10m"][i]
                for i in indexes
                if hourly.get("wind_speed_10m")
                and hourly["wind_speed_10m"][i] is not None
            ]

            output.append(
                f"DATE: {requested_date}"
            )

            if temperatures:
                output.append(
                    f"Average Temperature: "
                    f"{sum(temperatures) / len(temperatures):.1f} °C"
                )

                output.append(
                    f"Maximum Temperature: "
                    f"{max(temperatures):.1f} °C"
                )

                output.append(
                    f"Minimum Temperature: "
                    f"{min(temperatures):.1f} °C"
                )

            if humidity:
                output.append(
                    f"Average Humidity: "
                    f"{sum(humidity) / len(humidity):.1f} %"
                )

            if precipitation:
                output.append(
                    f"Total Precipitation: "
                    f"{sum(precipitation):.2f} mm"
                )

            if rain:
                output.append(
                    f"Total Rain: "
                    f"{sum(rain):.2f} mm"
                )

            if wind:
                output.append(
                    f"Maximum Wind: "
                    f"{max(wind):.1f} km/h"
                )

            output.append("")

        output.append(
            "DATA SOURCE: "
            "Open-Meteo Forecast API "
            "(past_days)"
        )

        return "\n".join(output)

    # ==================================================
    # OLDER HISTORICAL WEATHER
    # Open-Meteo ERA5 API
    # ==================================================

    historical_params = {

        "latitude": latitude,

        "longitude": longitude,

        "start_date": start_date,

        "end_date": end_date,

        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_mean",
            "precipitation_sum",
            "rain_sum",
            "snowfall_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "relative_humidity_2m_mean",
            "shortwave_radiation_sum",
            "et0_fao_evapotranspiration",
        ],

        "timezone": "auto",
    }

    try:

        response = requests.get(
            HISTORICAL_URL,
            params=historical_params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:
        return (
            f"Historical weather service error: "
            f"{e}"
        )

    daily = data.get("daily", {})

    dates = daily.get("time", [])

    if not dates:
        return (
            "No historical weather data "
            "was returned."
        )

    # --------------------------------------------------
    # FORMAT
    # --------------------------------------------------

    output = []

    output.append(
        "HISTORICAL WEATHER"
    )

    output.append(
        f"Location: {city}, {country}"
    )

    output.append(
        f"Coordinates: "
        f"{latitude}, {longitude}"
    )

    output.append(
        f"Period: "
        f"{start_date} to {end_date}"
    )

    output.append("")

    for i, weather_date in enumerate(dates):

        output.append(
            f"DATE: {weather_date}"
        )

        output.append(
            f"Average Temperature: "
            f"{daily['temperature_2m_mean'][i]} °C"
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
            f"Average Feels Like: "
            f"{daily['apparent_temperature_mean'][i]} °C"
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
            f"Snowfall: "
            f"{daily['snowfall_sum'][i]} cm"
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
            f"Average Humidity: "
            f"{daily['relative_humidity_2m_mean'][i]} %"
        )

        output.append(
            f"Solar Radiation: "
            f"{daily['shortwave_radiation_sum'][i]} MJ/m²"
        )

        output.append(
            f"Evapotranspiration: "
            f"{daily['et0_fao_evapotranspiration'][i]} mm"
        )

        output.append("")

    output.append(
        "DATA SOURCE: "
        "Open-Meteo ERA5 Historical API"
    )

    return "\n".join(output)