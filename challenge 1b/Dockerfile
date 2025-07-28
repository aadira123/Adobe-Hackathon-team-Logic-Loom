# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container's working directory.
# This assumes your Dockerfile is in the 'adobe hackathon' directory,
# and 'src', 'pdfs', 'output' are subdirectories of it.
COPY . .

# Expose any ports if your application were a web service (not applicable here, but good practice)
# EXPOSE 8000

# Command to run the application
# We're running main.py inside the 'src' directory
# The PDFs are expected in the 'pdfs' directory relative to WORKDIR,
# which matches the absolute paths you've set in main.py
# Make sure to set the PDF_DIR and OUTPUT_DIR in main.py to relative paths
# if you want to use the 'pdfs' and 'output' folders within the Docker container's /app directory.
# Current main.py has absolute paths, so we will adjust that for Docker.

# Revert PDF_DIR and OUTPUT_DIR in main.py to relative paths for Docker:
# PDF_DIR = "./pdfs/"
# OUTPUT_DIR = "./output/"

# The command to run your script
CMD ["python", "src/main.py"]