FROM alpine:latest

WORKDIR /app

RUN apk add --no-cache \
    curl \
    wget \
    git \
    bash \
    jq \
    ca-certificates

COPY . .

CMD ["sh", "-c", "echo 'Monolith decomposition analysis environment ready. Mount your source code and analysis scripts to /app.' && ls -la /app"]