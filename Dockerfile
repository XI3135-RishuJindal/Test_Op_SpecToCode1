# Use the official Python image from the Docker Hub pinned to version 3.12
FROM python:3.12-slim as base

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Expose the desired port
EXPOSE 8080

# Define the command to run the application
CMD ["python", "app.py"]