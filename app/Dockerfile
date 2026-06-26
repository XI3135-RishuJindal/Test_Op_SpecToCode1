# syntax=docker/dockerfile:1
FROM node:20-alpine AS base

WORKDIR /app

# Install production dependencies only
COPY package*.json ./
RUN npm ci --omit=dev

# Copy application source
COPY src/ ./src/

# ── Runtime ───────────────────────────────────────────────────────────────────
FROM base AS runtime

ENV NODE_ENV=production \
    PORT=3000

EXPOSE 3000

# Run as non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

CMD ["node", "src/index.js"]
