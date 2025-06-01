# Use the latest .NET SDK image as the build image
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Clone the Azure MCP source code
RUN git clone https://github.com/Azure/azure-mcp.git .

# Modify global.json to use the SDK version available in the container
RUN sed -i 's/"9.0.*"/"9.0"/' global.json

# Publish the application for ARM64
FROM build AS publish
RUN pwsh "eng/scripts/Build-Module.ps1" -OutputPath /app/publish -OperatingSystem Linux -Architecture arm64

# Build the runtime image
FROM mcr.microsoft.com/dotnet/aspnet:9.0-bookworm-slim AS runtime
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    apt-transport-https \
    lsb-release \
    gnupg \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && rm -rf /var/lib/apt/lists/*

# Copy the published application
COPY --from=publish "/app/publish/linux-arm64/dist" .

# Set environment variables
ENV MCP_SERVER_NAME="azure-mcp-server"
ENV ASPNETCORE_ENVIRONMENT="Production"

# Create startup script
RUN echo '#!/bin/bash\necho "Azure MCP Server ready"\ntail -f /dev/null' > /app/start.sh && chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
