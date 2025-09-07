# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . /app

# Create virtual environment & install Python dependencies
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Collect static files (for Django)
RUN . /opt/venv/bin/activate && python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the app with Gunicorn
CMD ["/opt/venv/bin/gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]



