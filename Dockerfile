
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project

COPY src/ ./src/
COPY sql/ ./sql/

CMD ["uv", "run", "--no-sync", "python", "src/pipeline.py"]
