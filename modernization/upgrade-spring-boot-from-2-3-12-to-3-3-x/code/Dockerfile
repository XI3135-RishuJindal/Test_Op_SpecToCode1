```
# Use the official Maven image to build the application
FROM maven:3.9.4-eclipse-temurin-21 AS build

# Set the working directory
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Use the official Eclipse Temurin JDK base image for Java 21
FROM eclipse-temurin:21-jre

# Set the working directory
WORKDIR /app

# Copy the jar file from the build stage
COPY --from=build /app/target/*.jar app.jar

# Expose the desired port
EXPOSE 8080

# Run the application
CMD ["java", "-jar", "app.jar"]
```