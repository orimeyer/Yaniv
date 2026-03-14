# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies for GUI (Tkinter/X11)
RUN apt-get update && apt-get install -y \
    python3-tk \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the GUI file instead of main.py
CMD ["python", "gui.py"]