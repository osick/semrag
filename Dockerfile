FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies for unstructured and file processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY pyproject.toml .
# We'll generate uv.lock during build if it doesn't exist, 
# but ideally it should be committed.
# COPY uv.lock . 

# Install dependencies using uv
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Create necessary directories
RUN mkdir -p /app/src /app/data /app/tests

COPY src /app/src
COPY tests /app/tests
COPY .env .

# Set Python path
ENV PYTHONPATH=/app/src

# Expose API and FastMCP ports
EXPOSE 8000
EXPOSE 8001

# Start the FastAPI server (which will now include the FastMCP and Upload API)
CMD ["uv", "run", "uvicorn", "src.semrag.api.openai_wrapper:app", "--host", "0.0.0.0", "--port", "8000"]
