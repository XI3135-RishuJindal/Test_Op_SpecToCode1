FROM alpine:latest

WORKDIR /app

COPY . .

RUN echo "No specific runtime detected. Add your build steps here."

CMD ["sh"]