FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create __init__.py files
RUN find . -type d -exec touch {}/__init__.py \;

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Start command - Railway uses PORT env variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
