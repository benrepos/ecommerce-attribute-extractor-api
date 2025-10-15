# Use official Python slim image
FROM python:3.11-slim

# Prevents Python from writing pyc files and enables unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8080

# Create entrypoint script to handle PORT env var
RUN echo '#!/bin/sh\nexec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Start FastAPI with uvicorn using the Cloud Run $PORT
ENTRYPOINT ["/entrypoint.sh"]
