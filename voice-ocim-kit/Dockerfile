# OCIM Bridge Dockerfile
# SC COOL BITS SRL - Voice to OCIM Bridge

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ocim_bridge.py .
COPY env.voice .

# Create non-root user
RUN useradd -m -u 1000 bridge && chown -R bridge:bridge /app
USER bridge

# Expose port
EXPOSE 7071

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7071/health || exit 1

# Start command
CMD ["python", "ocim_bridge.py"]
