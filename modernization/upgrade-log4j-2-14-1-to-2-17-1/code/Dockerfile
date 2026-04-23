```
# Use the official minimal base image for Java 21
FROM eclipse-temurin:21-jre as base

# Build stage
FROM maven:3-eclipse-temurin-21 AS build
WORKDIR /app

# Copy the pom.xml and download the dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the source code into the image
COPY src ./src

# Package the application
RUN mvn clean package -DskipTests

# Final stage
FROM base
WORKDIR /app

# Copy JAR file from the build stage
COPY --from=build /app/target/*.jar app.jar

# Expose the application port
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```