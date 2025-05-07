FROM openjdk:17-slim

WORKDIR /user
ADD ./build/libs/user-0.0.1-SNAPSHOT.jar /user/user.jar

EXPOSE 8081

CMD ["java", "-jar", "user.jar"]