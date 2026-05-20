# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure stdout/stderr are unbuffered for real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements explicitly first to leverage Docker layer caching
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code into the container
COPY . /app/

# Expose port 8005 for the Daphne web server
EXPOSE 8005

# Start the Daphne ASGI server, listening on all interfaces (0.0.0.0)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8005", "config.asgi:application"]
