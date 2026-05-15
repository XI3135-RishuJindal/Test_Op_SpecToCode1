FROM ubuntu:24.04

# Set environment variables for noninteractive install
ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies for CI workflows: build-essential, git, curl, and python3/pip for basic linting/testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Use /workspace as the working directory
WORKDIR /workspace

# Copy project files
COPY . /workspace

# Set default command (override in your CI as needed)
CMD ["/bin/bash"]