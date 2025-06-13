FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    UDL_BASE_URL=https://unifieddatalibrary.com \
    KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
    KAFKA_SECURITY_PROTOCOL=SASL_SSL \
    KAFKA_SASL_MECHANISM=PLAIN \
    INTEGRATION_INTERVAL=60 \
    LOG_LEVEL=INFO

# Run the integration
CMD ["python", "-m", "asttroshield.udl_integration.integration"] 