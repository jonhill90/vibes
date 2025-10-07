# Source: infra/task-manager/frontend/Dockerfile
# Pattern: Vite dev server Dockerfile with hot reload
# Extracted: 2025-10-07
# Relevance: 10/10 - Frontend Dockerfile for development with Vite

# Frontend development Dockerfile for Task Management UI
# Pattern: Vite dev server with hot reload
FROM node:20-alpine

WORKDIR /app

# Install system dependencies for npm packages
RUN apk add --no-cache python3 make g++ git curl

# Copy package files
COPY package*.json ./

# CRITICAL: Use npm ci for reproducible builds (not npm install)
RUN npm ci

# Copy source code
COPY . .

# Expose port 3000 for Vite dev server
EXPOSE 3000

# CRITICAL: --host flag required for Vite to work in Docker
# Without --host, Vite only listens on localhost inside the container
CMD ["npm", "run", "dev", "--", "--host"]
