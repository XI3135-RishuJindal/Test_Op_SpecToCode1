# syntax=docker/dockerfile:1

FROM alpine:latest

WORKDIR /app

COPY . /app

CMD ["sh"]