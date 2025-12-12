# DocQA-MS ML Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download pre-trained models (optional - can be done in training)
# RUN python -c "from transformers import AutoTokenizer, AutoModel; \
#     AutoTokenizer.from_pretrained('camembert-base'); \
#     AutoModel.from_pretrained('camembert-base')"

# Copy application code
COPY app/ ./app/

# Create directories with proper permissions
RUN mkdir -p saved_models data logs model_cache && \
    chmod -R 777 saved_models data logs model_cache

# Create non-root user
RUN useradd --create-home --shell /bin/bash mluser && \
    chown -R mluser:mluser /app
USER mluser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
