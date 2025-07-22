# pdf-unmerger-frontend/Dockerfile
# Stage 1: Build the React application
FROM node:18-alpine as builder

WORKDIR /app

# Copy package.json and package-lock.json (for npm)
COPY package.json package-lock.json ./
# Use npm install to install dependencies
RUN npm install --frozen-lockfile

COPY . .
# Use npm run build to build the application
RUN npm run build

# Stage 2: Serve the built application with Nginx
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html

# Expose the port Nginx listens on
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]