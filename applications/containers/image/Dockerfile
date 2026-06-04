# Use a specific Python image instead of ubuntu + python installation
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies in a single layer
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        iputils-ping \
        dnsutils \
        iproute2 \
        jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /coffeeshop

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /coffeeshop

# Switch to non-root user
USER appuser

# Expose port (adjust as needed)
EXPOSE 8080

# Use exec form and combine ENTRYPOINT + CMD
CMD ["python3", "app.py"]
