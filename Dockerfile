FROM ubuntu:24.04

LABEL maintainer="ci-pipeline"
LABEL description="CI pipeline image with build, test, and SAST capabilities"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    unzip \
    jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

CMD ["/bin/bash"]