FROM python:3.11-slim

# LEVEL 6 UPGRADE: PLANETARY SCALE (Dockerized Microservice)
# This allows MiroFish OS to be deployed on AWS/GCP Kubernetes clusters globally.

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up the environment
ENV PYTHONUNBUFFERED=1
ENV OS_ENVIRONMENT="production"
ENV ENCODING="utf-8"

# We would copy requirements here, but for now we just copy the OS
COPY ./mirofish_os /app/mirofish_os

# The container will run the AGI Core by default
CMD ["python", "mirofish_os/sparky_core/agi_core.py"]