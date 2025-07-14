# Use the official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Create a non-root user and group for security
RUN groupadd --system celery && useradd --system --create-home --gid celery celery

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Set ownership to the non-root user
RUN chown -R celery:celery /app

# Switch to the non-root user
USER celery

# Run Celery (change this for worker or beat)
CMD ["celery", "-A", "core", "worker", "--loglevel=info"]
