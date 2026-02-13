FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m -u 1001 app && \
    mkdir -p /app /home/app/.cache/uv && \
    chown -R app:app /app /home/app

WORKDIR /app

COPY --chown=app:app pyproject.toml uv.lock ./

RUN uv venv && \
    uv sync --locked --no-dev

COPY --chown=app:app . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/home/app/.cache/uv \
    PATH="/app/.venv/bin:${PATH}" \

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]