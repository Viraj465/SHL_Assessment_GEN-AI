# Base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22.x and npm for the React frontend
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Copy backend requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install frontend dependencies and build
WORKDIR /my-app
RUN npm install --legacy-peer-deps
RUN npm run build

# Move back to main directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV HOST=0.0.0.0

# Expose the backend port
EXPOSE 7860

# Start command
CMD ["python", "app.py"]