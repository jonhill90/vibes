#!/bin/bash

# Check if vibes-network exists
if docker network ls --format "{{.Name}}" | grep -q "^vibes-network$"; then
    echo "vibes-network exists, using it"
    export DEVCONTAINER_NETWORK="vibes-network"
else
    echo "vibes-network does not exist, using default bridge network"
    export DEVCONTAINER_NETWORK="bridge"
fi

# Create a dynamic docker-compose file
envsubst < /usr/local/share/docker-compose.template.yml > /tmp/docker-compose.dynamic.yml
