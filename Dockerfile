# Base image
FROM python:3.11

# Install system dependencies as root
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22.x and npm for the React frontend as root
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory with appropriate permissions
WORKDIR /app
RUN chown appuser:appuser /app

# Copy application files with correct ownership
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser app.py route.py answers.json ./
COPY --chown=appuser:appuser my-app/ ./my-app/

# Set npm cache directory with correct permissions
RUN mkdir -p /home/appuser/.npm && \
    chown -R appuser:appuser /home/appuser/.npm

# Switch to non-root user
USER appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install uvicorn fastapi


# Build frontend
WORKDIR /app/my-app
RUN npm install --legacy-peer-deps && \
    npm install @vitejs/plugin-react --legacy-peer-deps && \
     npm run build

# Move back to main directory and set up static files
WORKDIR /app
RUN mkdir -p static && \
    cp -r my-app/dist/* static/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOST=0.0.0.0

# Expose the backend port
EXPOSE 7860

# Start command

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
