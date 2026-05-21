FROM alpine:latest

RUN apk add --no-cache \
    git \
    curl \
    bash \
    python3 \
    py3-pip \
    nodejs \
    npm \
    openjdk17-jre-headless

WORKDIR /app

COPY . .

CMD ["sh"]