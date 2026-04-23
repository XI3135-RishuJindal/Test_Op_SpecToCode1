```Dockerfile
# Use an official minimal base image for OpenJDK 21 for build stage
FROM eclipse-temurin:21-jdk AS build

# Set the working directory
WORKDIR /app

# Copy the Maven build files
COPY pom.xml ./
COPY src ./src

# Install Maven dependencies and build the application
RUN ./mvnw clean package -DskipTests

# Use a minimal JRE runtime for the final image
FROM eclipse-temurin:21-jre-alpine

# Set the working directory
WORKDIR /app

# Copy the packaged application from the build stage
COPY --from=build /app/target/*.jar app.jar

# Expose the port the app runs on
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```