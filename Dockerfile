FROM alpine:3.20

WORKDIR /app

CMD ["sh", "-c", "echo 'No application source detected. Provide an app and a Dockerfile tailored to your runtime.' && sleep 3600"]