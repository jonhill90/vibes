# Frontend development Dockerfile for Task Management UI
# Pattern: Vite dev server with hot reload
FROM node:20-alpine

WORKDIR /app

# Install system dependencies for npm packages
RUN apk add --no-cache python3 make g++ git curl

# Copy package files
COPY package*.json ./

# Use npm ci for reproducible builds
RUN npm ci

# Copy source code
COPY . .

# Expose port 3000 for Vite dev server
EXPOSE 3000

# Start Vite dev server with --host flag for Docker
CMD ["npm", "run", "dev", "--", "--host"]
