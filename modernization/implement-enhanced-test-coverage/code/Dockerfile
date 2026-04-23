```Dockerfile
# Use the official Maven image to compile and build the application
FROM maven:3.9.2-eclipse-temurin-21-alpine as builder

# Create app directory
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy source code and run the build
COPY src ./src
RUN mvn clean package -DskipTests

# Use the official Eclipse Temurin minimal JRE base image
FROM eclipse-temurin:21-jre-alpine

# Create non-root user and set work directory
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app

# Copy the jar file from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Change ownership and switch to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```