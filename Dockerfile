# Dockerfile
FROM python:3.11-slim

# System deps (TLS + git for VCS installs)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# Faster, reproducible installs
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib

# Install the SDK + analysis deps via extras
RUN pip install --upgrade pip setuptools wheel && \
    pip install "conductor-sdk[analysis] @ git+https://github.com/hts-lab/conductor-sdk@main"

# App files
WORKDIR /app
COPY runner.py /app/runner.py

# Default command: run the script referenced by SCRIPT_REL
CMD ["python", "-u", "runner.py"]
