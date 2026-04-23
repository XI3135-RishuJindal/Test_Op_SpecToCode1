```
# Use the official Maven base image for the build stage
FROM maven:3.9.5-eclipse-temurin-21 AS build

# Set working directory
WORKDIR /app

# Copy pom.xml and resolve dependencies
COPY pom.xml ./
RUN mvn dependency:go-offline

# Copy the rest of the project source
COPY src ./src

# Package the application
RUN mvn clean package -DskipTests

# Use the official JDK runtime base image for the run stage
FROM eclipse-temurin:21-jre

# Set working directory
WORKDIR /app

# Copy the packaged application from the build stage
COPY --from=build /app/target/*.jar app.jar

# Expose the application port
EXPOSE 8080

# Set the entry command
CMD ["java", "-jar", "app.jar"]
```