FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create application directory
WORKDIR /app

# Copy application code
COPY . .

# Run pytest tests
FROM base AS test
RUN pip install --no-cache-dir pytest pytest-mock pytest-cov
CMD ["pytest", "--cov=myapp", "tests"]

FROM base AS final

# Expose application port
EXPOSE 8080

# Set the executable command
CMD ["python", "app.py"]