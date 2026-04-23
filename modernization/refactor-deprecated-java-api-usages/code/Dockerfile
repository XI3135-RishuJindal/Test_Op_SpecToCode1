```
# Use an official Maven image to build the application
FROM maven:3.8-eclipse-temurin-21 as builder

WORKDIR /app

# Cache dependencies as a distinct layer
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the application code
COPY src ./src

# Build the application
RUN mvn package -DskipTests

# Use a minimal base image for Java 21 runtime
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy the built application from the builder stage
COPY --from=builder /app/target/*.jar /app/application.jar

# Run the application
CMD ["java", "-jar", "/app/application.jar"]
```