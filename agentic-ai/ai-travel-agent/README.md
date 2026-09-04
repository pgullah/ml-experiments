# AI Travel Agent

A command-line travel planner built with LangGraph and LangChain. It combines web
search, OpenWeather data, currency conversion, and budget calculations to produce
a conversational itinerary.

## Setup

Requires Python 3.12 or newer. Install dependencies with `uv sync`, then create a
`.env` file in either `agentic-ai/` or `agentic-ai/ai-travel-agent/` containing:

```dotenv
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openrouter/free
OPENWEATHERMAP_API_KEY=...
SERPER_API_KEY=...    # optional; DuckDuckGo is used as a fallback
TAVILY_API_KEY=...    # optional
```

If both files exist, the project-local `ai-travel-agent/.env` takes precedence.

Configuration is validated once at startup by `AppSettings`. Optional operational
settings include `PROMPT_DIR`, `OPENAI_API_KEY`, `OPENAI_MODEL`,
`MAX_CONTEXT_MESSAGES`, `MAX_CONTEXT_CHARACTERS`, `MAX_REQUEST_CHARACTERS`,
`OPENWEATHERMAP_API_URL`, `SERPER_API_URL`, `TAVILY_API_URL`,
`SEARCH_MAX_RESULTS`, `CURRENCY_API_URL`, and `REQUEST_TIMEOUT_SECONDS`.

Run the chat interface:

```shell
uv run python main.py
```

Enter `exit` or `quit` to stop. OpenWeather supplies forecasts for at most five
days; requests outside that window should be treated as seasonal guidance rather
than a current forecast.

## Tests

```shell
uv run pytest
```

Run a single feature or include coverage:

```shell
uv run pytest tests/features/test_conversation.py
uv run pytest --cov=app --cov-report=term-missing
```
