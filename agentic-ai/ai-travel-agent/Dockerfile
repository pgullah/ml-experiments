FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Cache dependency installation separately from application changes.
COPY pyproject.toml README.md ./
RUN uv sync --no-dev --group ui --no-install-project

RUN useradd --create-home --uid 10001 appuser
COPY app/ ./app/
COPY prompts/ ./prompts/
COPY api.py main.py streamlit_app.py ./

USER appuser
EXPOSE 8000 8501

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
