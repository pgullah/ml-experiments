# AI Travel Agent

A command-line travel planner built with LangGraph and LangChain. It combines web
search, OpenWeather data, currency conversion, and budget calculations to produce
a conversational itinerary.

## Setup

Requires Python 3.12 or newer. Install dependencies with `uv sync`, copy
`.env.example` to `.env`, and replace the placeholder credentials. A `.env` may
live in either `agentic-ai/` or `agentic-ai/ai-travel-agent/`:

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
`MAX_GUARD_THREADS`, `MAX_CONVERSATION_MESSAGES`, `GRAPH_RECURSION_LIMIT`,
`DOMAIN_CONFIDENCE_THRESHOLD`, `SEARCH_MAX_OUTPUT_CHARACTERS`,
`OPENWEATHERMAP_API_URL`, `SERPER_API_URL`, `TAVILY_API_URL`,
`SEARCH_MAX_RESULTS`, `CURRENCY_API_URL`, and `REQUEST_TIMEOUT_SECONDS`.

Run the chat interface:

```shell
uv run python main.py
```

After installation, the equivalent console command is `uv run travel-agent`.

Enter `exit` or `quit` to stop. OpenWeather supplies forecasts for at most five
days; requests outside that window should be treated as seasonal guidance rather
than a current forecast.

Run the Streamlit UI by installing its optional dependency group:

```shell
uv sync --group ui
uv run --group ui streamlit run streamlit_app.py
```

Use **New conversation** in the sidebar to clear the current session. Each UI
session owns a separate agent instance and thread ID.

## Runtime behavior and limitations

- Search results and price information are evidence, not confirmed booking
  availability. Verify flights, rooms, tickets, visa rules, restrictions, and
  final prices with the relevant official provider.
- Conversation messages, search output, guard context, request size, HTTP
  duration, and graph steps are bounded through `AppSettings`.
- The default `InMemorySaver` preserves context only for the lifetime of the
  process. Supply a durable LangGraph checkpointer to `Agent` when persistence
  across restarts is required.
- `app.prompt.prompt_router.route` is an optional, typed prompt-selection API.
  It requires `OPENAI_API_KEY`; it is not called by the primary travel agent.
- Before exposing the UI publicly, place it behind authentication and
  infrastructure-level rate limiting. Never log `.env` contents or provider
  credentials.

## Tests

```shell
uv run pytest
```

Run a single feature or include coverage:

```shell
uv run pytest tests/features/test_conversation.py
uv run pytest --cov=app --cov-report=term-missing
```

Run all local quality checks:

```shell
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=85
```
