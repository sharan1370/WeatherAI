from tools.weather_tools import (
    get_current_weather,
)


if __name__ == "__main__":

    print("=" * 60)
    print("OPEN-METEO CURRENT WEATHER TEST")
    print("=" * 60)

    result = get_current_weather.run(
        "Chennai"
    )

    print()
    print(result)

    print()
    print("=" * 60)