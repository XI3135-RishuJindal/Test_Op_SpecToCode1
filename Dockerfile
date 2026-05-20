FROM ubuntu:24.04

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

# Install common tooling
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

CMD ["/bin/bash"]