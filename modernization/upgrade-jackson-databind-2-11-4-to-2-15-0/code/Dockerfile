FROM eclipse-temurin:21-jre as base

WORKDIR /app
COPY target/myapp.jar /app/myapp.jar

FROM maven:3.8-eclipse-temurin-21 as build

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn package -DskipTests

FROM base

COPY --from=build /app/target/myapp.jar /app/myapp.jar
ENTRYPOINT ["java", "-jar", "/app/myapp.jar"]