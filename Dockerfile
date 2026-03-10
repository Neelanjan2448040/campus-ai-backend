# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# gcc and other build essentials might be needed for some python packages like bcrypt or mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using uvicorn
# Using uvicorn directly for FastAPI. 
# --proxy-headers is useful if running behind a reverse proxy like Nginx
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
