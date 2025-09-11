# CoolBits.ai Docker Configuration
# ===============================

FROM python:3.11-slim

# Set non-interactive environment
ENV CI=1
ENV NO_COLOR=1
ENV GCLOUD_SUPPRESS_PROMPTS=1
ENV CLOUDSDK_CORE_DISABLE_PROMPTS=1
ENV GIT_TERMINAL_PROMPT=0
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Create non-root user
RUN useradd -m -u 1000 coolbits && chown -R coolbits:coolbits /app
USER coolbits

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose ports
EXPOSE 8080 8100

# Start script
COPY scripts/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]