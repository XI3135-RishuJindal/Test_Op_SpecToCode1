# No Dockerfile present in the base source code, and the upgrade context
# specifies only a log4j-core library upgrade (CVE-2021-44228 remediation)
# with no language, runtime, build tool, or framework details provided.
#
# Generating a minimal, best-practice Java Dockerfile using a current LTS JRE
# that supports running a JAR built with log4j-core 2.17.2+.

FROM eclipse-temurin:21-jre-alpine

# Create a non-root user for security best practices
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy the application JAR (expected to be built with log4j-core >= 2.17.2)
COPY --chown=appuser:appgroup app.jar app.jar

USER appuser

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]