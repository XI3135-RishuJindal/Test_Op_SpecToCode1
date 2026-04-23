```
# Use a multi-stage build for Java application with Maven

# Stage 1: Build the application
FROM maven:3.8.5-eclipse-temurin-21 as builder

# Set the working directory
WORKDIR /app

# Copy the pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Stage 2: Run the application
FROM eclipse-temurin:21-jre

# Set the working directory
WORKDIR /app

# Copy the built jar file from the builder stage
COPY --from=builder /app/target/myapp.jar .

# Expose the port the application will run on
EXPOSE 8080

# Set the command to run the application
CMD ["java", "-jar", "myapp.jar"]
```