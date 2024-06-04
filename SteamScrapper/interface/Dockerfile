# interface/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the environment variables
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the Flask application
CMD ["python", "app.py"]

