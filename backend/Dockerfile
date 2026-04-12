FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets PORT env var (default 8080)
# config.py reads this and main.py uses it
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
