FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install mcp python-dotenv

WORKDIR /workspace
COPY server.py /workspace/
COPY .env /workspace/

CMD ["python3", "/workspace/server.py"]
