# ArcaneOS Backend Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY core/ ./core/
COPY ArcaneOS/ ./ArcaneOS/

# Copy startup script
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Create directories for state files and audio cache
RUN mkdir -p /app/data /app/arcane_audio

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check (using httpx which is already in requirements)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)"

# Run the application using startup script (handles Railway PORT)
CMD ["./start.sh"]
