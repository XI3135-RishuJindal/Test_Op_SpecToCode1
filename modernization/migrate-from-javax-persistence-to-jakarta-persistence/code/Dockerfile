```dockerfile
# Use an official minimal base image for Java 21
FROM eclipse-temurin:21-jre as base

# Use a Maven image to build the application
FROM maven:3.9-eclipse-temurin-21-alpine as builder

# Set the working directory for the build
WORKDIR /app

# Copy the pom.xml and any other necessary files
COPY pom.xml /app/

# Download Maven dependencies
RUN mvn dependency:go-offline

# Copy the entire project source
COPY . /app/

# Build the application with Maven
RUN mvn clean package -DskipTests

# Final stage for minimal runtime image
FROM base

# Set the working directory for the application
WORKDIR /app

# Copy the built jar from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Expose the application port
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```