# Use an official Python runtime as the base image
FROM python:3.9  

# Set the working directory in the container
WORKDIR /app

# Set the display environment variable
ENV DISPLAY=:99  

# Copy the requirements file into the container
COPY requirements.txt .

# Install system dependencies for pygame
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    xvfb \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y xvfb gunicorn

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser

# Set ownership and permissions for the app directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Create the game_result.txt file
RUN touch /app/game_result.txt

# Set executable permissions for the game script
RUN chmod +x /app/breaker_game.py

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application with Gunicorn
CMD ["xvfb-run","gunicorn", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
