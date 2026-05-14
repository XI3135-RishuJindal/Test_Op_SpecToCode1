FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

COPY . .

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app /app
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]