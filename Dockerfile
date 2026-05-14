FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv, pip, setuptools, wheel if needed
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt

COPY . /app

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]