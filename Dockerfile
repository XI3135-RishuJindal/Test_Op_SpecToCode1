# Dockerfile for a generic application adding health and readiness endpoints

# Using a lightweight base image for Python as an example
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run application
CMD ["python", "app.py"]

# Health and readiness endpoints should be implemented in the application itself (e.g., Flask, FastAPI, etc.), and doesn't require specific Docker instructions. 
# The CMD instruction here assumes that the Python script/app will handle HTTP requests for health and readiness.