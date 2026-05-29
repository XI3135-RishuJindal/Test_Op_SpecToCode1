FROM alpine:latest

WORKDIR /app

COPY . .

CMD ["sh", "-c", "echo 'Documentation container running' && ls -la"]