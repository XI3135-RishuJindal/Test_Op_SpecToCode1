FROM eclipse-temurin:21-jre as runtime

WORKDIR /app

COPY target/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]