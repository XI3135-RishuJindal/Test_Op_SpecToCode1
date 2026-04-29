FROM python:3.12-slim AS base

FROM base AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels Flask

FROM base
WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --find-links=/wheels Flask
COPY . .
CMD ["flask", "run", "--host=0.0.0.0"]