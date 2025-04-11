# Base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm for the React frontend
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Copy backend requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install frontend dependencies and build
WORKDIR /app/my-app
RUN npm install
RUN npm run build

# Move back to main directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Expose ports for both backend and frontend
EXPOSE 7860
EXPOSE 3000

# Start command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]