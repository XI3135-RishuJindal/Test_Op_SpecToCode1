# ── Build stage ───────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /workspace

COPY pom.xml .
COPY src ./src

# Download dependencies first (layer caching)
RUN apk add --no-cache maven && \
    mvn dependency:go-offline -B

# Build the fat JAR, skip tests (tests run in CI)
RUN mvn package -DskipTests -B

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jre-alpine AS runtime

LABEL maintainer="pharmacy-team"
LABEL org.opencontainers.image.title="pharmacy-microservice"
LABEL org.opencontainers.image.description="Pharmacy Microservice — prescriptions, adherence, price comparison"

# Non-root user for security
RUN addgroup -S pharmacy && adduser -S pharmacy -G pharmacy

WORKDIR /app

COPY --from=builder /workspace/target/pharmacy-microservice-*.jar app.jar

RUN chown pharmacy:pharmacy app.jar

USER pharmacy

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:8080/api/v1/health || exit 1

ENTRYPOINT ["java", \
    "-XX:+UseContainerSupport", \
    "-XX:MaxRAMPercentage=75.0", \
    "-Djava.security.egd=file:/dev/./urandom", \
    "-jar", "app.jar"]
