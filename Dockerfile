FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install application dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set default command (override as needed)
CMD ["python", "app.py"]