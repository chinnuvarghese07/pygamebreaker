# Use an official Python runtime as the base image
FROM python:3.9  

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for pygame and Xvfb
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

# Install the required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables for SDL (video and audio)
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy

# Set executable permissions for the game script
RUN chmod +x breaker_game.py

# Expose the port the app runs on
EXPOSE 5000

# Run Xvfb and the application
CMD ["xvfb-run", "gunicorn", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
