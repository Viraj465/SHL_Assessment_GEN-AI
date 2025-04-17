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
    && npm install -g npm@latest \
    && npm install -g axios

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory with appropriate permissions
WORKDIR /app
RUN chown appuser:appuser /app

# Copy and install Python dependencies
COPY --chown=appuser:appuser requirements.txt .

# Switch to non-root user
USER appuser

RUN pip install --no-cache-dir -r requirements.txt

# Copy files with correct ownership
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser app.py route.py answers.json ./
COPY --chown=appuser:appuser my-app/ ./my-app/

# Copy backend files to /app
COPY app/ ./app/
COPY app.py route.py answers.json ./
# COPY README.md  ./

# Copy frontend files to /my-app
COPY my-app/ ./my-app/

WORKDIR /app/my-app

# Now build the frontend
RUN if [ -f "package.json" ]; then \
    npm install --legacy-peer-deps && \
    npm run build; \
    else \
    echo "No package.json found in /my-app"; \
    exit 1; \
    fi

# Move back to main directory
WORKDIR /app
RUN mkdir -p static
RUN cp -r my-app/build/* static/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV HOST=0.0.0.0

# Expose the backend port
EXPOSE 7860

# Start command
CMD ["python", "app.py"]