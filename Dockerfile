# Use the official Python 3.12.2 slim runtime image
FROM python:3.12.2-slim

# Install dependencies for mysqlclient package
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config


# Copy the Django project to the container
COPY . /app

# Set the working directory inside the container
WORKDIR /app

# Set environment variables
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Create the Python virtual environment
RUN python3 -m venv /opt/venv

# Upgrade pip, install all dependencies and set entrypoint script as executable
RUN /opt/venv/bin/python -m pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    chmod +x entrypoint.sh && \
    chmod +x /app/migrate.sh
