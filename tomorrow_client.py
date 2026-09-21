import os

import requests
from dotenv import load_dotenv


load_dotenv()

TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")

BASE_URL = "https://api.tomorrow.io/v4/weather/realtime"


def get_current_weather(
    latitude: float,
    longitude: float,
):
    """Get current weather from Tomorrow.io."""

    if not TOMORROW_API_KEY:
        raise ValueError(
            "TOMORROW_API_KEY is not configured."
        )

    params = {
        "location": f"{latitude},{longitude}",
        "apikey": TOMORROW_API_KEY,
        "units": "metric",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":

    print("=" * 60)
    print("TOMORROW.IO API TEST")
    print("=" * 60)

    # Chennai coordinates
    latitude = 13.0827
    longitude = 80.2707

    try:

        data = get_current_weather(
            latitude,
            longitude,
        )

        print("\nAPI connection successful!")

        print("\nRaw response:")

        print(data)

    except requests.exceptions.HTTPError as e:

        print("\nHTTP ERROR:")
        print(e)

        if e.response is not None:
            print(
                "\nAPI response:"
            )
            print(e.response.text)

    except Exception as e:

        print("\nERROR:")
        print(e)