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

## REST API

Set `TRAVEL_AGENT_API_KEY` in `.env` to a separate service secret, alongside the
provider credentials. From `agentic-ai/ai-travel-agent/`, run:

```shell
uv sync
uv run uvicorn api:app --host 0.0.0.0 --port 8000 --workers 1
```

Interactive documentation is at http://localhost:8000/docs. `GET /health` returns
`{"status":"ok"}` without authentication and does not probe external providers.
`POST /chat` requires a bearer token:

```shell
curl http://localhost:8000/chat \
  -H 'Authorization: Bearer YOUR_SERVICE_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Plan three days in Rome","thread_id":"telegram:123456"}'
```

The response is `{"content":"...","thread_id":"telegram:123456"}`. Reuse the
thread ID for follow-ups; use a new ID to start a fresh conversation. Your bot
should derive IDs from trusted Telegram chat/user metadata. The service token
grants access to all conversations, so keep it in your bot backend.

Requests require a nonblank `message` (up to `MAX_REQUEST_CHARACTERS`) and
`thread_id` (up to 256 characters). Invalid input returns 422; invalid or missing
authentication returns 401. Domain refusals and the agent's safe fallback replies
use the normal 200 response schema. Unhandled failures return a generic 500.

This initial API processes one chat request at a time. Concurrent requests receive
503 with `Retry-After: 1`; the bot should queue messages per conversation and retry
busy responses with backoff. Calls are synchronous and may take multiple provider
requests to finish. Acknowledge Telegram webhooks before processing in a worker.
Deduplicate Telegram updates in the bot; this API does not implement request IDs
or retry deduplication. Avoid automatically retrying ambiguous timeouts.

Run one worker and one replica: conversation history and guard context live in
memory and are lost on restart. Shared persistence and concurrency coordination
are needed before scaling. Keep the API on a private network, or use HTTPS when
calling across hosts.

## Docker

From `agentic-ai/ai-travel-agent/`, build and start the REST API:

```shell
docker build -t ai-travel-agent .
docker run --rm --env-file .env -p 8000:8000 ai-travel-agent
```

Open http://localhost:8000/docs. Create `.env` from `.env.example` and fill in your
credentials before running; environment files are excluded from the image.
If your `.env` lives in `agentic-ai/`, use `--env-file ../.env` instead.

To start Streamlit instead:

```shell
docker run --rm --env-file .env -p 8501:8501 ai-travel-agent \
  streamlit run streamlit_app.py --server.address=0.0.0.0 --server.headless=true
```

To run the command-line chat with the same image:

```shell
docker run --rm -it --env-file .env ai-travel-agent python main.py
```

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
