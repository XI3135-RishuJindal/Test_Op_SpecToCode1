FROM --platform=linux/amd64 <official-minimal-base-image>:latest AS builder

WORKDIR /app
COPY . .

# Assume an unknown build command for the application
RUN <build-command>

FROM --platform=linux/amd64 <official-minimal-base-image>:latest

WORKDIR /app
COPY --from=builder /app .

CMD ["<start-command>"]