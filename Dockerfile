FROM alpine:latest

# Set working directory
WORKDIR /app

# Copy source code
COPY . /app

# Install runtime prerequisites (example: curl, replace with actual app dependencies as needed)
RUN apk add --no-cache curl

# Set non-root user for security best practice (create user if needed)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Expose port (example, adjust as appropriate)
EXPOSE 8080

# Entrypoint with environment variable support for secrets
CMD ["sh", "-c", "echo 'App started. Configure secrets via environment variables.' && sleep infinity"]