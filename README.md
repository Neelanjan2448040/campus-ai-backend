# 🎓 Campus-AI Backend

A robust, production-ready FastAPI backend for Comprehensive Campus Management, featuring role-based access control, academic tracking, and an integrated AI Chatbot with persistent memory.

## 🚀 Key Features

### 🏢 Campus Management
*   **Authentication**: Secure JWT-based authentication for both Students and Administrators.
*   **Student Portal**: Profile management, grade tracking, and attendance monitoring.
*   **Admin Dashboard**: Restricted operations to add students, list all users, update academic marks, and manage attendance records.
*   **Course System**: Dynamic course creation, faculty assignment, and tracking of assignments/tests.
*   **Leave Management**: Integrated system for faculty and students to apply for leaves.

### 🤖 AI Chatbot (Groq & MongoDB)
*   **Role-Based Personality**: The chatbot behaves differently for students (Academic Support) and admins (Faculty Assistant).
*   **Persistent Memory**: Uses **MongoDB** to store and retrieve the last 10 messages for each user, providing a context-aware conversational experience.
*   **LLM Integration**: Powered by **Groq's Llama-3.1-8b-instant** model for high-speed, intelligent responses.

---

## 🛠️ Technology Stack
*   **Framework**: FastAPI (Python)
*   **SQL Database**: MySQL with SQLAlchemy ORM
*   **NoSQL Database**: MongoDB with Motor (for AI memory)
*   **AI Engine**: Groq Cloud API
*   **Containerization**: Docker & Docker Hub

---

## 🐳 Docker Setup (Recommended)
The project is fully containerized for easy deployment and consistent environments.

### 1. Build and Run
```powershell
# Build the image
docker build -t campus-ai-backend .

# Run the container (using Docker-specific environment variables)
docker run -p 8000:8000 --env-file .env.docker campus-ai-backend
```

### 2. Docker Hub Deployment
```powershell
# Tag the image
docker tag campus-ai-backend your_username/campus-ai-backend:v1.0

# Push to Docker Hub
docker push your_username/campus-ai-backend:v1.0
```

---

## ⚙️ Local Development
If you prefer running without Docker:

### 1. Requirements
*   Python 3.10+
*   MySQL Server
*   MongoDB Server

### 2. Installation
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Run the project
python main.py
```

### 3. Environment Config
Ensure you have a `.env` file for local development and a `.env.docker` file for Docker development. Use `.env.example` as a template for both.

---

## 📋 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/students/login` | Student login to receive JWT |
| POST | `/admins/login` | Admin login to receive JWT |
| POST | `/chat` | **AI Assistant (Supports memory & role-context)** |
| GET | `/admin/students` | List all registered students (Admin only) |
| GET | `/courses` | List all available courses |

---

## 📖 Documentation
Once the server is running, access the interactive API documentation at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---
*Developed with focus on stability, scalability, and modern DevOps practices.*
