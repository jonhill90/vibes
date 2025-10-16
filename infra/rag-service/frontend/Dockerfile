# RAG Service Frontend - Docker Image
# Development build with hot reload

FROM node:20-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Run Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
