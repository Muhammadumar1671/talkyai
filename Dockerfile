# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    python3-dev \
    pkg-config \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python3.11 manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Apply database migrations and run the application
CMD ["sh", "-c", "python3.11 manage.py migrate && python3.11 manage.py runserver 0.0.0.0:8000"]
