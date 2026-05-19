# syntax=docker/dockerfile:1

FROM alpine:latest AS base

WORKDIR /app

COPY . /app

# Install common test tools; adjust as needed per language
RUN apk add --no-cache bash curl

CMD ["/bin/sh"]