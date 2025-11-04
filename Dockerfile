# Dockerfile — Python 3.11 slim, builds wheels where needed
FROM python:3.11-slim

WORKDIR /app

# Install build tools for packages that need compilation
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends build-essential python3-dev gcc g++ cargo libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt requirements-server.txt /app/

# Upgrade pip tooling and install deps
RUN python -m pip install --upgrade pip setuptools wheel packaging && \
    if [ -f requirements-server.txt ]; then pip install -r requirements-server.txt; else pip install -r requirements.txt; fi

# Copy project files
COPY . /app

# Expose port (adjust to your app)
EXPOSE 8000

# Default start command — adjust if your entrypoint differs
CMD ["python3", "app.py"]
