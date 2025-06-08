# Stage 1: Build React app
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve static files with http-server
FROM node:18-alpine AS production
WORKDIR /app
RUN npm install -g http-server
COPY --from=build /app/build /app/build
EXPOSE 3000
# Run http-server to serve the React app
CMD ["http-server", "build", "-p", "3000"]