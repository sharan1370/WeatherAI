from crew.weather_crew import weather_crew
if __name__ == "__main__":
    print("=" * 60)
    print("🌤️ WEATHER AI ASSISTANT")
    print("=" * 60)
    question = input(
        "\nAsk a weather question: "
    )
    result = weather_crew.kickoff(
        inputs={
            "question": question
        }
    )
    print()
    print("=" * 60)
    print("🌤️ WEATHER ASSISTANT")
    print("=" * 60)
    print(result)
    print("=" * 60)