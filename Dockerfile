FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc curl tzdata && \
    ln -snf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Sao_Paulo

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml ./

RUN uv lock && uv sync --no-dev

ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .

EXPOSE 8000

CMD if [ "$MODE" = "background" ]; then \
    echo "Starting background worker..." && \
    python -m app.background_main; \
    else \
    echo "Starting FastAPI server..." && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000; \
    fi
