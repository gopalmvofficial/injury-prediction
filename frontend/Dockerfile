# Stage 1: Build React application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (cached if package files don't change)
COPY package*.json ./
RUN npm install

# Copy source files
COPY . .

# Build argument for backend API URL (optional override)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the production bundle
RUN npm run build

# Stage 2: Serve application with Nginx
FROM nginx:alpine

# Remove default nginx html
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
