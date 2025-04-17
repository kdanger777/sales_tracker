# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

EXPOSE 5000

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install setuptools first (this provides distutils)
RUN pip install --no-cache-dir setuptools wheel

# Install pip requirements
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install debugpy

WORKDIR /app
COPY . /app

# Create data directory and set permissions
RUN mkdir -p /app/data && \
    chmod 777 /app/data

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
