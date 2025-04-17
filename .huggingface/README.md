---
title: SHL Assessment
emoji: 🚀
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
app_file: app.py
pinned: false
---

# SHL Assessment Application

A sophisticated FastAPI and React-based application for providing SHL assessment recommendations using AI.

## Features
- AI-powered assessment recommendations
- Interactive user interface built with React
- FastAPI backend for efficient data processing
- FAISS vector store for similarity search
- Docker containerization for easy deployment

## Project Structure
```
SHLapp/
├── app/                    # Main application directory
│   ├── api/               # FastAPI backend
│   │   ├── data/         # Data files and vector stores
│   │   └── routes/       # API endpoints
│   └── frontend/         # React frontend
├── Dockerfile            # Docker configuration
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### Local Development
1. Clone the repository:
```bash
git clone https://huggingface.co/spaces/Viraj0112/SHL_Assessment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.api.main:app --reload
```

### Docker Deployment
1. Build the Docker image:
```bash
docker build -t shl-assessment .
```

2. Run the container:
```bash
docker run -p 7860:7860 shl-assessment
```

## Environment Variables
- `PORT`: Application port (default: 7860)
- Add other relevant environment variables

## API Documentation
- Access the API documentation at `/docs` endpoint
- Detailed API endpoints and usage

## Contributing
[Add contribution guidelines if applicable]

## License
[Add license information]