```dockerfile
# Use a Maven image for building the application
FROM maven:3.8.8-eclipse-temurin-21 AS builder

# Set working directory
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the application source code
COPY src ./src

# Build the application
RUN mvn package -DskipTests

# Use a minimal base image for running the application
FROM eclipse-temurin:21-jre

# Set working directory
WORKDIR /app

# Copy the Spring Boot jar file from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Expose the port the app runs on
EXPOSE 8080

# Set the startup command to run the jar file
ENTRYPOINT ["java", "-jar", "app.jar"]
```