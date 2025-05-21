FROM openjdk:17-slim

WORKDIR /files
ADD ./build/libs/files-0.0.1-SNAPSHOT.jar /files/files.jar

EXPOSE 8082

CMD ["java", "-jar", "files.jar"]