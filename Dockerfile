FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Flask (typically 5000)
EXPOSE 5000

# Use a non-root user for security
RUN useradd -m appuser
USER appuser

# Set entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]