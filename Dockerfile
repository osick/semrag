FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for unstructured and file processing
RUN apt-get update && apt-get install -y 
    build-essential 
    libpq-dev 
    libmagic1 
    poppler-utils 
    tesseract-ocr 
    libreoffice 
    pandoc 
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src /app/data /app/tests

COPY src /app/src
COPY tests /app/tests
COPY .env .

# Set Python path to include 'src'
ENV PYTHONPATH=/app/src

# Expose the OpenAI-compatible API port
EXPOSE 8000

# Start the FastAPI server using uvicorn
CMD ["uvicorn", "src.semrag.api.openai_wrapper:app", "--host", "0.0.0.0", "--port", "8000"]
