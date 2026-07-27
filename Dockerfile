FROM debian:bookworm-slim

WORKDIR /app

COPY . .

CMD ["sh"]