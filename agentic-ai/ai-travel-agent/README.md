# AI Travel Agent

A command-line travel planner built with LangGraph and LangChain. It combines web
search, OpenWeather data, currency conversion, and budget calculations to produce
a conversational itinerary.

## Setup

Requires Python 3.12 or newer. Install dependencies with `uv sync`, then create a
`.env` file containing:

```dotenv
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openrouter/free
OPENWEATHERMAP_API_KEY=...
SERPER_API_KEY=...    # optional; DuckDuckGo is used as a fallback
TAVILY_API_KEY=...    # optional
```

Run the chat interface:

```shell
uv run python main.py
```

Enter `exit` or `quit` to stop. OpenWeather supplies forecasts for at most five
days; requests outside that window should be treated as seasonal guidance rather
than a current forecast.

## Tests

```shell
uv run python -m unittest discover -s tests -v
```
