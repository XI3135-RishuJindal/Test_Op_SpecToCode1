# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Keeps Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies in a separate layer for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose the default service port
EXPOSE 5000

# Run with gunicorn in production; override CMD for development
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]
