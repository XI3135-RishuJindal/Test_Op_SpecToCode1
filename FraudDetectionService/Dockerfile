# Use OpenJDK image
FROM openjdk:11-jre-slim

# Set the working directory inside the container
WORKDIR /app

# Copy application JAR
COPY target/fraud-detection-service.jar /app/fraud-detection-service.jar

# Expose the application port
EXPOSE 8080

# Run the JAR file
ENTRYPOINT ["java", "-jar", "/app/fraud-detection-service.jar"]