FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend

# Honor $PORT if set, default to 8080 (works on Cloud Run and anywhere else)
CMD ["sh","-c","uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]