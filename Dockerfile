FROM alpine:latest

WORKDIR /app

COPY . .

RUN echo "No specific runtime detected. Add your application files and build steps here." && \
    echo "Example: RUN apk add --no-cache <your-runtime>" && \
    ls -la

CMD ["sh", "-c", "echo 'Container started. Configure CMD for your application.' && sleep infinity"]