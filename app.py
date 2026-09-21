
import streamlit as st

from crew.weather_crew import weather_crew


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WeatherAI",
    page_icon="🌤️",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🌤️ WeatherAI")

    st.caption("Intelligent Weather Assistant")

    st.divider()

    st.subheader("💡 Example Questions")

    examples = [
        "What is the weather in Chennai now?",
        "Will it rain tomorrow in Chennai?",
        "Give me the 7 day forecast for Chennai",
        "What was the weather in Chennai yesterday?",
        "What was the weather in Chennai in 2020?",
    ]

    for example in examples:

        if st.button(
            example,
            use_container_width=True,
        ):

            st.session_state.example_question = example
            st.rerun()

    st.divider()

    st.subheader("🌐 Data Sources")

    st.write("☁️ Open-Meteo Weather API")
    st.write("🤖 CrewAI Agent")
    st.write("🧠 Groq LLM")

    st.success("Weather services available")

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🌤️ WeatherAI")

st.write(
    "Your intelligent weather information assistant"
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.info(
        """
        ### ✨ Weather Intelligence

        Ask questions about current weather,
        future forecasts, or historical weather.

        WeatherAI uses real weather data from
        Open-Meteo and uses Groq to explain
        the retrieved information.
        """
    )

    st.subheader("What can I help you with?")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.container(border=True)

        st.markdown("### 🌡️ Current Weather")

        st.write(
            "Get current temperature, humidity, "
            "wind, precipitation, visibility "
            "and UV information."
        )

    with col2:

        st.container(border=True)

        st.markdown("### 🌦️ Weather Forecast")

        st.write(
            "Check tomorrow's weather or get "
            "forecasts for the coming days."
        )

    with col3:

        st.container(border=True)

        st.markdown("### 📊 Historical Weather")

        st.write(
            "Explore yesterday's weather, recent "
            "weather, or older historical periods."
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# WEATHER FUNCTION
# ============================================================

def get_weather_answer(question):

    with st.chat_message("assistant"):

        with st.spinner(
            "🌤️ Checking weather information..."
        ):

            try:

                result = weather_crew.kickoff(
                    inputs={
                        "question": question
                    }
                )

                answer = str(result)

                if "rate-limit" in answer.lower() or "rate limiting" in answer.lower():
                    answer = (
                        "**Open-Meteo is temporarily rate-limiting this deployment.**\n\n"
                        "Please wait a few minutes before trying again. "
                        "The weather service is currently unavailable for this server."
                    )

            except Exception as error:

                answer = (
                    "⚠️ **Unable to retrieve weather information.**\n\n"
                    f"Error: `{error}`"
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ============================================================
# EXAMPLE QUESTION FROM SIDEBAR
# ============================================================

if "example_question" in st.session_state:

    question = st.session_state.example_question

    del st.session_state.example_question

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    get_weather_answer(question)


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask about the weather..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    get_weather_answer(question)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌤️ WeatherAI • CrewAI • Groq • Open-Meteo"
)

