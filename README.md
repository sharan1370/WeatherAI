# WeatherAI

WeatherAI is a Python weather assistant that combines CrewAI, Groq, Streamlit, and Open-Meteo. A user asks a natural-language weather question, a CrewAI agent selects the correct weather tool, the tool retrieves real API data, and Groq explains the result.

The project supports:

- Current weather
- Future forecasts from tomorrow through 16 days
- Recent historical weather
- Older historical weather from the Open-Meteo ERA5 archive
- A Streamlit chat interface
- A command-line interface

## Table Of Contents

1. [A-Z Guide](#a-z-guide)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Run The Application](#run-the-application)
7. [How A Request Works](#how-a-request-works)
8. [Weather Tools](#weather-tools)
9. [Project Structure](#project-structure)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)
13. [Limitations](#limitations)

## A-Z Guide

### A - Application

The main user interface is `app.py`, a Streamlit chat application. `main.py` provides a terminal alternative.

### B - Backend APIs

The weather data backend is Open-Meteo. It provides geocoding, current weather, forecasts, recent past weather, and ERA5 historical data.

### C - CrewAI

CrewAI manages the agent and task. `crew/weather_crew.py` creates one sequential crew containing the weather agent and weather task.

### D - Data Sources

The project uses:

- Open-Meteo geocoding API for city-to-coordinate lookup
- Open-Meteo forecast API for current and future weather
- Open-Meteo forecast API with `past_days` for recent historical weather
- Open-Meteo ERA5 archive API for older historical weather
- Groq for natural-language explanation

### E - Environment Variables

The required secret is `GROQ_API_KEY`. It is loaded from `.env` using `python-dotenv`. The application model is fixed in code to `openai/gpt-oss-20b`.

### F - Forecasts

The forecast tool accepts a requested number of days and limits it to 1 through 16. It skips today's row and returns future daily values.

### G - Groq

CrewAI uses the LiteLLM-compatible identifier `groq/openai/gpt-oss-20b`. The underlying Groq model is exactly `openai/gpt-oss-20b`.

### H - Historical Weather

Historical requests are validated, geocoded, and routed to either recent past data or the ERA5 archive based on the requested date range.

### I - Installation

Install the dependencies from `requirements.txt` inside a Python virtual environment. Details are in [Installation](#installation).

### J - JSON APIs

The weather tools call JSON endpoints with `requests`, check HTTP errors, read the response JSON, and format the result as text for the agent.

### K - Knowledge Boundary

The agent is instructed not to invent weather values or rely on internal model knowledge when a weather value is requested. Numerical values must come from a weather tool.

### L - LLM Compatibility

CrewAI's installed LiteLLM path can add an internal `cache_breakpoint` field that Groq rejects. `agents/weather_agents.py` defines `GroqLLM`, which removes that internal field before the request is sent.

### M - Model

The only application model is:

```text
openai/gpt-oss-20b
```

Do not replace it with another model unless the agent configuration and user requirement are intentionally changed together.

### N - Natural Language

Users do not need to call tools directly. They can ask questions such as `What is the weather in Chennai now?` or `What was the weather in London on 2020-01-15?`.

### O - Open-Meteo

Open-Meteo supplies the factual weather data. It does not require an API key for the calls used by this project.

### P - Python

The project targets Python 3.12 or newer.

### Q - Questions

The agent classifies questions into current, forecast, or historical weather before calling a tool.

### R - Routing

Routing is performed by the CrewAI agent according to the instructions in `tasks/weather_tasks.py`.

### S - Streamlit

The Streamlit UI stores the conversation in `st.session_state`, displays example questions, and sends each question to `weather_crew.kickoff(...)`.

### T - Tools

The three registered tools are:

- `Current Weather Tool`
- `Weather Forecast Tool`
- `Historical Weather Tool`

### U - User Flow

The user enters a question, waits while the crew executes, and receives a formatted response containing the relevant location, date or time, measurements, and data source.

### V - Validation

The tools validate locations, date formats, date order, future historical dates, and forecast day limits. Network requests use timeouts and return readable error strings.

### W - Weather Values

Depending on the request, the response can include temperature, feels-like temperature, humidity, wind, gusts, precipitation, rain, showers, cloud cover, visibility, pressure, UV index, sunrise, sunset, and weather code.

### X - External Services

The application needs internet access for both Groq and Open-Meteo. A local model server is not required.

### Y - Your Questions

Useful examples:

```text
What is the weather in Chennai now?
Will it rain tomorrow in Chennai?
Give me the 7 day forecast for Chennai.
What was the weather in Chennai yesterday?
What was the weather in Chennai on 2020-01-15?
```

### Z - Zero Fabrication

When an API fails or a location cannot be found, the tool returns an error message. The agent must not fill missing values with guesses.

## Architecture

### High-Level Architecture

```mermaid
flowchart TD
    User[User] --> UI[Streamlit app.py]
    User --> CLI[CLI main.py]
    UI --> Crew[CrewAI weather_crew]
    CLI --> Crew
    Crew --> Task[weather_task]
    Task --> Agent[Weather Intelligence Specialist]
    Agent --> Current[Current Weather Tool]
    Agent --> Forecast[Weather Forecast Tool]
    Agent --> Historical[Historical Weather Tool]
    Current --> OpenMeteo[Open-Meteo APIs]
    Forecast --> OpenMeteo
    Historical --> OpenMeteo
    OpenMeteo --> ToolResult[Formatted weather data]
    ToolResult --> Agent
    Agent --> Groq[Groq: openai/gpt-oss-20b]
    Groq --> Answer[Natural-language answer]
    Answer --> UI
    Answer --> CLI
```

### Request Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend or CLI
    participant C as CrewAI Crew
    participant A as Weather Agent
    participant G as Geocoding API
    participant W as Weather API
    participant L as Groq

    U->>F: Enter weather question
    F->>C: kickoff(question)
    C->>A: Execute weather task
    A->>A: Classify current, forecast, or historical
    A->>G: Resolve city to coordinates
    G-->>A: Coordinates and timezone
    A->>W: Request weather data
    W-->>A: JSON weather data
    A->>L: Explain tool result
    L-->>C: Final weather answer
    C-->>F: Crew output
    F-->>U: Display answer
```

### Agent Decision Flow

```mermaid
flowchart TD
    Start[Weather question] --> Location[Identify location]
    Location --> Type{What type of request?}
    Type -->|Current or now| Current[Current Weather Tool]
    Type -->|Tomorrow or future| Forecast[Weather Forecast Tool]
    Type -->|Yesterday or past date| Historical[Historical Weather Tool]
    Current --> Explain[Groq explains retrieved data]
    Forecast --> Explain
    Historical --> Explain
    Explain --> Final[Final answer with source and values]
```

### Historical Data Routing

```mermaid
flowchart TD
    Request[Historical request] --> Validate[Validate YYYY-MM-DD dates]
    Validate --> Valid{Valid and not future?}
    Valid -->|No| Error[Return validation error]
    Valid -->|Yes| Age{Date range within recent 10 days?}
    Age -->|Yes| Recent[Forecast API with past_days]
    Age -->|No| Archive[ERA5 archive API]
    Recent --> Format[Format historical result]
    Archive --> Format
    Format --> Agent[Return result to CrewAI agent]
```

### Deployment Shape

```mermaid
flowchart LR
    Browser[User browser] --> Streamlit[Streamlit process]
    Streamlit --> CrewAI[CrewAI and LiteLLM]
    CrewAI --> Groq[Groq API]
    CrewAI --> Meteo[Open-Meteo APIs]
    Env[Environment secrets] --> Streamlit
```

## Requirements

- Python 3.12 or newer
- `pip` or `uv`
- A valid Groq API key
- Internet access
- A supported operating system for Python and Streamlit

Runtime dependencies are listed in [requirements.txt](requirements.txt) and [pyproject.toml](pyproject.toml):

- `crewai`
- `python-dotenv`
- `requests`
- `streamlit`
- `langchain-groq`
- `litellm`

## Installation

### Windows PowerShell

```powershell
cd C:\weather_prediction_done
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation for the current terminal, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate the environment again.

### macOS or Linux

```bash
cd weather_prediction_done
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root. Never commit a real API key.

```env
GROQ_API_KEY=your_groq_api_key
```

The application always uses:

```text
openai/gpt-oss-20b
```

The model is pinned in `agents/weather_agents.py`; no model override is required in `.env`.

## Run The Application

### Streamlit Web App

```powershell
streamlit run app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

The web app provides:

- A chat input
- Conversation history for the current browser session
- Example questions in the sidebar
- A clear conversation button
- Current, forecast, and historical weather workflows

### Command-Line App

```powershell
python main.py
```

Enter one question when prompted. The result is printed in the terminal.

### Direct Tool Checks

```powershell
python test_tools.py
python test_forecast.py
python test_historical.py
```

These scripts call weather tools directly without asking the LLM to route the request.

## How A Request Works

1. `app.py` or `main.py` receives the question.
2. The frontend or CLI calls `weather_crew.kickoff(inputs={"question": question})`.
3. `weather_task` tells the agent to classify the request.
4. The agent chooses one registered weather tool.
5. The selected tool geocodes the location.
6. The tool calls the appropriate Open-Meteo endpoint.
7. The tool formats API values into readable text.
8. Groq explains the factual tool result.
9. CrewAI returns the final answer to the frontend or CLI.

## Weather Tools

### Current Weather Tool

Defined in `tools/weather_tools.py`.

Input:

```text
location: city name
```

Process:

1. Search the Open-Meteo geocoding endpoint.
2. Select the first matching location.
3. Request current weather using latitude, longitude, and automatic timezone.
4. Return current conditions.

The result can contain temperature, feels-like temperature, humidity, dew point, wind, precipitation, cloud cover, visibility, pressure, UV index, weather code, and whether it is day or night.

### Weather Forecast Tool

Defined in `tools/forecast_tools.py`.

Input:

```text
location: city name
forecast_days: integer from 1 through 16
```

The tool requests one extra day so it can skip today and return the requested future days. It returns daily minimum and maximum temperatures, precipitation, rain probability, wind, gusts, UV index, sunrise, and sunset.

### Historical Weather Tool

Defined in `tools/historical_tools.py`.

Input:

```text
location: city name
start_date: YYYY-MM-DD
end_date: YYYY-MM-DD
```

The tool rejects invalid dates, reversed ranges, and future dates. Recent requests use the forecast API's `past_days` option. Older requests use the Open-Meteo ERA5 archive API.

## Project Structure

```text
weather_prediction_done/
|-- app.py                         Streamlit web application
|-- main.py                        Command-line application
|-- pyproject.toml                 Project metadata and dependencies
|-- requirements.txt               pip dependency list
|-- README.md                      This documentation
|-- .env                           Local secrets; do not commit
|-- tomorrow_client.py             Optional Tomorrow.io example client
|-- agents/
|   `-- weather_agents.py          Agent and Groq compatibility adapter
|-- config/
|   `-- settings.py                Configuration placeholder
|-- crew/
|   `-- weather_crew.py            Crew composition
|-- tasks/
|   `-- weather_tasks.py           Routing and answer instructions
`-- tools/
    |-- weather_tools.py           Current weather tool
    |-- forecast_tools.py          Forecast tool
    |-- historical_tools.py        Historical weather tool
    `-- test_historical.py         Tool-level historical check
```

## Important Modules

### `agents/weather_agents.py`

Creates the weather agent, registers all weather tools, loads environment values, and pins the model to `openai/gpt-oss-20b`. `GroqLLM` removes CrewAI's internal cache marker before LiteLLM sends the request to Groq.

### `tasks/weather_tasks.py`

Defines the classification rules and expected answer format. The task requires the agent to use real tool output and avoid invented numbers.

### `crew/weather_crew.py`

Creates a sequential CrewAI crew with the weather agent and weather task.

### `app.py`

Creates the Streamlit page, manages chat session state, handles example questions, calls the crew, and displays errors in the UI.

## Testing

### Configuration Check

```powershell
python test_config.py
```

This reports whether `GROQ_API_KEY` is loaded and prints the configured test model value.

### Groq API Check

```powershell
python test_groq.py
```

This sends a direct request to the Groq OpenAI-compatible endpoint. It requires `GROQ_API_KEY` and internet access.

### Weather API Checks

```powershell
python test_tools.py
python test_forecast.py
python test_historical.py
```

These checks require internet access to Open-Meteo. They are smoke tests rather than isolated unit tests.

### Syntax Check

```powershell
python -m py_compile app.py main.py agents/weather_agents.py crew/weather_crew.py tasks/weather_tasks.py tools/weather_tools.py tools/forecast_tools.py tools/historical_tools.py
```

## Deployment

### Streamlit Community Cloud

1. Push the project to a Git repository.
2. Create a Streamlit Community Cloud app.
3. Select the repository and `app.py` as the entry point.
4. Add `GROQ_API_KEY` in the app's Secrets settings.
5. Deploy using `requirements.txt`.

Do not upload `.env` or place the API key in source code.

### Docker-Style Deployment

The process needs Python dependencies, a listening Streamlit server, and the Groq secret. A typical command inside a container is:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Set `GROQ_API_KEY` through the platform's secret manager or environment configuration.

### Other Platforms

The same deployment pattern works on Render, Railway, Azure, AWS, or another Python host:

- Install `requirements.txt`.
- Set `GROQ_API_KEY` securely.
- Start `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT` when the platform supplies `PORT`.
- Allow outbound HTTPS access to Groq and Open-Meteo.

## Troubleshooting

### `GROQ_API_KEY` is missing

Confirm that `.env` exists in the project root and that the virtual environment is active. For deployment, add the key to the hosting platform's secrets instead of relying on `.env`.

### CrewAI cannot initialize `groq/openai/gpt-oss-20b`

Install the dependencies again:

```powershell
pip install -r requirements.txt
```

The `litellm` package is required because this CrewAI configuration uses a Groq model identifier through LiteLLM.

### Groq rejects `cache_breakpoint`

Use the project's `GroqLLM` adapter in `agents/weather_agents.py`. It removes CrewAI's internal cache marker before the Groq request. Do not replace it with a raw `ChatGroq` object in `Agent(llm=...)` for this CrewAI version.

### A location cannot be found

Try a more specific location, such as:

```text
Chennai, India
London, United Kingdom
```

The geocoding service uses the first matching result.

### Historical date errors

Use `YYYY-MM-DD`, make sure the start date is not after the end date, and do not request a future date.

### Streamlit starts but answers fail

Check the terminal logs, verify the Groq key, verify internet access, and run the direct checks:

```powershell
python test_config.py
python test_groq.py
python test_tools.py
```

### Port 8501 is already in use

Start Streamlit on another port:

```powershell
streamlit run app.py --server.port 8502
```

## Security Notes

- Keep `GROQ_API_KEY` out of Git.
- Use platform secret storage in production.
- Do not print or log the API key.
- Open-Meteo responses are external data and should be treated as untrusted input.
- The application is a prototype and does not provide authentication or user accounts.

## Limitations

- Weather requests require internet access.
- The first geocoding result is used when multiple locations match.
- The Streamlit conversation is stored only in the current session.
- The project does not persist users, queries, or results.
- Smoke tests call live external services and can fail because of network or service availability.
- CrewAI's verbose execution logs can be lengthy during debugging.

## Quick Start

```powershell
cd C:\weather_prediction_done
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_groq_api_key
```

Start the app:

```powershell
streamlit run app.py
```

Then ask:

```text
What is the weather in London right now?
```

## License And API Terms

Review the current terms and usage limits for CrewAI, Groq, Streamlit, and Open-Meteo before deploying the project commercially. This repository does not include a separate license declaration.
