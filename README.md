# Campus-AI Backend

A robust FastAPI backend for the Campus Management System, featuring role-based access control, academic tracking, and an integrated AI Chatbot with persistent memory.

## Architecture & Tech Stack

- **Framework**: FastAPI (Python)
- **Database (Relational)**: MySQL via SQLAlchemy ORM
- **Database (NoSQL)**: MongoDB via Motor (for AI chat memory)
- **AI Integrations**: Groq Cloud API
- **Containerization**: Docker

## Core Subsystems

### Campus Administration
- Secure JWT-based authentication for Students and Administrators.
- Profile management, grade tracking, and attendance monitoring for students.
- Restricted operations for administrators to add students, list users, update marks, and manage attendance.

### Course & Leave Management
- Dynamic course creation, faculty assignment, and tracking of assignments/tests.
- Integrated system for faculty and students to apply for leaves.

### AI Chatbot Engine
- Role-based responses configured for Student support vs. Admin support.
- Utilizes MongoDB to store and retrieve the trailing message history for contextual awareness.
- Powered by LLMs via Groq infrastructure.

## Deployment Instructions

The backend is fully containerized. It is designed to be run via Docker Compose alongside the frontend, but can also be run in isolation using Docker.

### Running via Docker
```bash
# Build the image
docker build -t campus-ai-backend .

# Run the container attached to local environment configuration
docker run -p 8000:8000 --env-file .env.docker campus-ai-backend
```

## Local Development Setup

If you need to run the application bare-metal for development:

1. **System Requirements**: 
   - Python 3.10+
   - Running instances of MySQL and MongoDB.

2. **Environment Configuration**:
   - Create a `.env` file based on `.env.example` in the root directory.

3. **Install and Run**:
```bash
# Initialize and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start the uvicorn development server
python main.py
```

## Interactive Documentation

Once the server is running, FastAPI automatically generated interactive Swagger/OpenAPI documentation.
Access the API endpoints and test requests at:
`http://localhost:8000/docs`
