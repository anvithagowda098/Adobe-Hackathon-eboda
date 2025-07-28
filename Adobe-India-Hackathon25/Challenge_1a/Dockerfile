FROM --platform=linux/amd64 python:3.10-slim

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY main.py ./

# Create input and output directories
RUN mkdir -p input output

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]