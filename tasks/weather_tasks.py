from crewai import Task
from agents.weather_agents import weather_agent
weather_task = Task(
    description="""
You are answering this user question:
{question}
Determine what type of weather information
the user is requesting.
There are three possibilities:
1. CURRENT WEATHER
   Examples:
   - What is the weather in Chennai now?
   - What is the temperature in Chennai?
   - How humid is Chennai right now?
   Use:
   Current Weather Tool
2. FUTURE WEATHER / FORECAST
   Examples:
   - What will the weather be tomorrow?
   - What is the forecast for Chennai?
   - Will it rain tomorrow?
   - Give me the weather for the next 7 days.
   Use:
   Weather Forecast Tool
3. HISTORICAL WEATHER
   Examples:
   - What was the weather yesterday?
   - What was Chennai weather on January 15, 2020?
   - What was the temperature in Chennai in 2022?
   Use:
   Historical Weather Tool
IMPORTANT RULES:
- Always use a weather tool when real weather
  information is requested.
- Never invent weather values.
- Never use your internal knowledge as a replacement
  for live weather data.
- Do not claim that the model predicted the weather.

- The weather API provides the actual numerical
  weather/forecast data.

- Groq should only explain the retrieved data.

- If the user gives a location, identify it correctly.

- If the user provides a specific historical date,
  use that date.

- If the user asks for a future period, retrieve
  forecast data.

- If the question is ambiguous, clearly explain
  what information is available.
""",

    expected_output="""
A concise and accurate natural-language weather answer.

The answer must:

- Use the weather tool result.
- Include the location.
- Include the relevant date/time.
- Include temperature when available.
- Include other relevant weather information.
- Never invent numerical values.
- Clearly distinguish historical data from forecasts.
""",
    agent=weather_agent,
)
