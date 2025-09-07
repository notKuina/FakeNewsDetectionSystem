# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
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

# Run app with Gunicorn
CMD ["/opt/venv/bin/gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
