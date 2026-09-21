from tools.forecast_tools import (
    get_weather_forecast,
)


if __name__ == "__main__":

    print("=" * 60)
    print("OPEN-METEO FORECAST TEST")
    print("=" * 60)

    result = get_weather_forecast.run(
        "Chennai",
        7,
    )

    print()
    print(result)

    print("=" * 60)