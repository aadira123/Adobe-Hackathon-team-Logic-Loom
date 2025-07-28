# Use a slim Python image for smaller size and AMD64 compatibility
FROM --platform=linux/amd64 python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script into the container
COPY main.py .

# Create input and output directories as expected by the challenge
# The main.py script expects these specific paths inside the container.
RUN mkdir -p /app/input /app/output

# Command to run the application when the container starts
# The script will automatically process all PDFs from /app/input directory
# and save the results to /app/output.
CMD ["python", "main.py"]
