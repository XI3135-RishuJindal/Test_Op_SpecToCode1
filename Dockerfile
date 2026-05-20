FROM alpine:latest

WORKDIR /app

COPY . .

RUN echo "No build step defined. Add your build instructions here."

CMD ["echo", "No runtime command defined. Update CMD with your application entrypoint."]