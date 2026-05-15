# syntax=docker/dockerfile:1
FROM ubuntu:24.04

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# Install basic utilities and Python3 for unittests as a common denominator
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        ca-certificates \
        git \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project files (modify as needed if precise context known)
COPY . /app

# Install dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip3 install --upgrade pip && pip3 install -r requirements.txt; fi

# Default command (overridden in real project as appropriate)
CMD [ "python3", "-m", "unittest", "discover" ]