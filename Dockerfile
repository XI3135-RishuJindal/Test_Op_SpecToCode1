FROM debian:12.6-slim

WORKDIR /app

CMD ["sh", "-lc", "echo 'No application source provided. Add your app and update this Dockerfile accordingly.' && sleep infinity"]