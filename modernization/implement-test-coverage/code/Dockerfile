FROM --platform=linux/amd64 ubuntu:latest AS builder

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    build-essential \
    && make build

FROM --platform=linux/amd64 ubuntu:latest AS final

WORKDIR /app

COPY --from=builder /app .

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && pip3 install pytest \
    && rm -rf /var/lib/apt/lists/*

CMD ["pytest"]