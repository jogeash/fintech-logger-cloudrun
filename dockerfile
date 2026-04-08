# Start from a slim Python 3.11 base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files into the container
COPY . .

# Cloud Run expects port 8080
EXPOSE 8080

# Use gunicorn to serve the Flask app (more stable than Flask dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]