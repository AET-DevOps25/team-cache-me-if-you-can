#!/bin/bash

set -e  # Exit on first error

echo "Building user service..."
cd ./server/user
./gradlew clean build -x test
cd ../../

echo "Building gateway service..."
cd ./server/gateway
./gradlew clean build -x test
cd ../../

echo "Building files service..."
cd ./server/files
./gradlew clean build -x test
cd ../../

echo "All JARs built successfully."
