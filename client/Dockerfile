# Stage 1: Build React app
FROM node:20-alpine AS build
WORKDIR /app
COPY client/package.json client/package-lock.json ./
RUN npm install
COPY client/ . 
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80