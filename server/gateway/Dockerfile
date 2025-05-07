FROM openjdk:17-slim

WORKDIR /gateway
ADD ./build/libs/gateway-0.0.1-SNAPSHOT.jar /gateway/gateway.jar

EXPOSE 8080

CMD ["java", "-jar", "gateway.jar"]