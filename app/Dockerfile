# syntax=docker/dockerfile:1
FROM eclipse-temurin:17-jdk-alpine AS builder

WORKDIR /workspace

COPY pom.xml .
COPY src ./src

# Download dependencies in a separate layer for better caching
RUN --mount=type=cache,target=/root/.m2 \
    ./mvnw -B dependency:go-offline -q 2>/dev/null || true

COPY mvnw .
COPY .mvn .mvn

RUN --mount=type=cache,target=/root/.m2 \
    ./mvnw -B package -DskipTests -q

# ── Runtime image ─────────────────────────────────────────────────────────────
FROM eclipse-temurin:17-jre-alpine AS runtime

# Non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

WORKDIR /app

COPY --from=builder /workspace/target/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:8080/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
