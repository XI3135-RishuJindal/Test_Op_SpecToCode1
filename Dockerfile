# Start from the latest stable Python image with slim variant for smaller size
FROM python:3.12-slim as base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create app directory
WORKDIR /app

# Install system dependencies and cleanup
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Set up entry point
CMD ["python", "app.py"]

# Multi-stage build for Bandit SAST and detect-secrets
FROM base as dev

# Install Bandit and detect-secrets for security analysis
RUN pip install --no-cache-dir bandit detect-secrets

# Execute Bandit and detect-secrets as part of the CI/CD pipeline
CMD ["bandit", "-r", "/app"]