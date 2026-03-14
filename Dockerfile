# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container at /app
# We do this first to leverage Docker's layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run the game when the container launches
# -it flag will be needed in the command line for user input
CMD ["python", "main.py"]