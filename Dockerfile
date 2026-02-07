FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port for web UI
EXPOSE 5000

# Default command - start FastAPI web server
# Can be overridden to use CLI: docker run podbotnik python cli.py chat --transcripts sample_transcripts.json
CMD ["python", "web.py", "sample_transcripts.json", "5000"]
