FROM openjdk:17-slim

WORKDIR /files
ADD ./build/libs/files-0.0.1-SNAPSHOT.jar /files/files.jar
ENV SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/files_database
ENV SPRING_DATASOURCE_USERNAME=files
ENV SPRING_DATASOURCE_PASSWORD=Files123!
EXPOSE 8082

CMD ["java", "-jar", "files.jar"]
