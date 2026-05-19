FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies in a separate layer if requirements.txt exists
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels -r requirements.txt

COPY . .

# Final minimal image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app /app

RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

CMD ["python", "app.py"]