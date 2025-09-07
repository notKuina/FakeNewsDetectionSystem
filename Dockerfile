# Base image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to backend
WORKDIR /app/backend

# Copy entire project
COPY . /app

# Copy dataset files explicitly
COPY ./backend/detection/data /app/backend/detection/data

# Create virtual environment & install Python dependencies + gunicorn
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r /app/requirements.txt \
    && /opt/venv/bin/pip install gunicorn

# Collect static files (Django)
RUN /opt/venv/bin/python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run app with Gunicorn (adjust Python path to your wsgi)
CMD ["/opt/venv/bin/gunicorn", "FakeNews.wsgi:application", "--chdir", "/app/backend", "--bind", "0.0.0.0:8000"]
