# Use an official Python runtime as a parent image
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for pyproj and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libproj-dev \
    proj-data \
    proj-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install runtime dependencies for pyproj
RUN apt-get update && apt-get install -y --no-install-recommends \
    libproj25 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder stage
COPY --from=builder /install /usr/local

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8040 available to the world outside this container
EXPOSE 8040

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run uvicorn when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8040"]
