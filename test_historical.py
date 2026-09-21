from tools.historical_tools import (
    get_historical_weather,
)
if __name__ == "__main__":

    print("=" * 60)
    print("OPEN-METEO HISTORICAL WEATHER TEST")
    print("=" * 60)

    result = get_historical_weather.run(
        "Chennai",
        "2020-01-15",
        "2020-01-15",
    )

    print()
    print(result)

    print("=" * 60)