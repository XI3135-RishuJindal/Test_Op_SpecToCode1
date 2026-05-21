FROM alpine:latest

WORKDIR /app

COPY . .

RUN echo "No specific runtime detected. Add your build and test commands here." && \
    echo "Example: apk add --no-cache <your-runtime>" && \
    echo "Example: <your-build-tool> build" && \
    echo "Example: <your-build-tool> test"

CMD ["sh", "-c", "echo 'No start command configured. Update CMD for your stack.'"]