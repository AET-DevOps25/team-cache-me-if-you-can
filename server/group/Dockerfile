FROM openjdk:17-slim

WORKDIR /group
ADD ./build/libs/group-0.0.1-SNAPSHOT.jar /group/group.jar

EXPOSE 8083

# Change CMD to entrypoint for more control and to catch early errors
# This will allow us to pass additional JVM arguments
ENTRYPOINT ["java", "-jar", "/group/group.jar"]
# We will pass specific command line arguments in docker-compose.yml for debugging