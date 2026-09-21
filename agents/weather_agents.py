from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai.llms.cache import CACHE_BREAKPOINT_KEY
from tools.weather_tools import get_current_weather
from tools.forecast_tools import get_weather_forecast
from tools.historical_tools import get_historical_weather

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"


class GroqLLM(LLM):
    def _format_messages_for_provider(self, messages):
        formatted_messages = super()._format_messages_for_provider(messages)
        return [
            {
                key: value
                for key, value in message.items()
                if key != CACHE_BREAKPOINT_KEY
            }
            for message in formatted_messages
        ]


groq_llm = GroqLLM(model=f"groq/{GROQ_MODEL}")

weather_agent = Agent(
    role="Weather Intelligence Specialist",
    goal=(
        "Answer weather questions using real weather "
        "data retrieved from the appropriate weather "
        "tool. Never invent weather information."
    ),
    backstory=(
        "You are an expert weather information "
        "assistant. You have access to current, "
        "forecast, and historical weather tools. "
        "You carefully identify whether the user "
        "is asking about current, future, or past "
        "weather and use the correct tool. "
        "You never guess weather values."
    ),
    tools=[
        get_current_weather,
        get_weather_forecast,
        get_historical_weather,
    ],
    llm=groq_llm,
    verbose=True,
    allow_delegation=False,
)
