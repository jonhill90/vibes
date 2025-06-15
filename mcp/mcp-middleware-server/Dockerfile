FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY claude_config_example.json .

EXPOSE 5001

CMD ["python", "server.py"]

