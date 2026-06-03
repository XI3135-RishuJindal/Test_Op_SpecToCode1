FROM alpine:latest

LABEL maintainer=""
LABEL description="Application container"

# Document required environment variables
# Copy and review .env.example for all required variables before running
# Required environment variables (set via -e, --env-file, or docker-compose environment):
#
#   APP_ENV        - Application environment (e.g. development, staging, production)
#   APP_PORT       - Port the application listens on (default: 8080)
#   APP_SECRET_KEY - Secret key for session/token signing (required, no default)
#   DATABASE_URL   - Full database connection string (required, no default)
#   LOG_LEVEL      - Logging verbosity (e.g. debug, info, warn, error; default: info)
#
# Optional environment variables:
#   TZ             - Timezone (default: UTC)
#   PUID           - User ID to run the process as (default: 1000)
#   PGID           - Group ID to run the process as (default: 1000)
#
# Local setup instructions:
#   1. Copy .env.example to .env and fill in all required values:
#        cp .env.example .env
#   2. Build the image:
#        docker build -t app:latest .
#   3. Run the container with your .env file:
#        docker run --env-file .env -p 8080:8080 app:latest
#   4. Or use docker-compose (recommended for local development):
#        docker-compose up --build

WORKDIR /app

# Set safe defaults for optional variables
ENV APP_ENV=production \
    APP_PORT=8080 \
    LOG_LEVEL=info \
    TZ=UTC

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "echo 'No start command configured. Set CMD in Dockerfile or override at runtime.' && exit 1"]