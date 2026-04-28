FROM eclipse-temurin:17-jre-alpine as runtime

WORKDIR /app

# Copy application jar and dependencies
COPY target/*.jar app.jar

# Upgrade log4j-core to 2.17.1 at runtime (for override); adjust if jar name is different
ADD https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.17.1/log4j-core-2.17.1.jar /app/log4j-core-2.17.1.jar

ENTRYPOINT ["java", "-cp", "log4j-core-2.17.1.jar:app.jar", "com.example.Main"]