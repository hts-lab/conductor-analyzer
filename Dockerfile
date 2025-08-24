# Dockerfile
FROM python:3.11-slim

# Install git so pip can pull from GitHub
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install the SDK (pin to a tag/commit when you have one)
RUN pip install --no-cache-dir "conductor-sdk @ git+https://github.com/hts-lab/conductor-sdk@main" \
    && pip install --no-cache-dir pandas numpy matplotlib google-cloud-storage

# App files
WORKDIR /app
COPY runner.py /app/runner.py

# Default command: run the script referenced by SCRIPT_REL
CMD ["python", "-u", "runner.py"]

