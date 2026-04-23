```
# Use the official OpenJDK 21 base image for the target runtime
FROM eclipse-temurin:21-jre as runtime

# Use a lightweight Maven image for building the application
FROM maven:3.9.4-eclipse-temurin-21 as build

# Set the working directory
WORKDIR /app

# Copy the pom.xml file to download dependencies
COPY pom.xml .

# Download dependencies
RUN mvn dependency:go-offline

# Copy the entire project to the working directory
COPY . .

# Build the application using Maven
RUN mvn clean package -DskipTests

# Use a minimal base image for the final stage
FROM eclipse-temurin:21-jre as final

# Set the working directory
WORKDIR /app

# Copy the built jar file from the build stage
COPY --from=build /app/target/*.jar app.jar

# Expose the application port
EXPOSE 8080

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```