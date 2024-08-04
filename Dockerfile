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

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the game_result.txt file and set permissions
RUN touch game_result.txt && chmod 666 game_result.txt

# Set environment variables for audio
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy

# Set executable permissions for the game script
RUN chmod +x breaker_game.py

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Create a non-root user and switch to it (optional but recommended)
RUN useradd -m appuser
USER appuser

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
