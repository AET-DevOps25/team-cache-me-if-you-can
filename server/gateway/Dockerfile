FROM openjdk:17-slim

WORKDIR /gateway
ADD ./build/libs/gateway-0.0.1-SNAPSHOT.jar /gateway/gateway.jar

EXPOSE 8080

CMD ["java", "-jar", "gateway.jar"]

ENV USER_SERVICE_URL=http://user:8081
ENV FILES_SERVICE_URL=http://files:8082
ENV GENAI_SERVICE_URL=http://genai:8000
