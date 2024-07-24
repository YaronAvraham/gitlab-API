# Use a minimal alpine image
FROM python:3.9-alpine

# Add any needed packages
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY api-gitlab.py .

# Install required Python packages
RUN pip install requests flask

# Expose the service on port 5000
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "api-gitlab.py"]
