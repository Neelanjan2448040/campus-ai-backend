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
*   **Memory Depth**: Remembers user specifics (like names) within the conversation window.

## 🛠️ Technology Stack
*   **Framework**: FastAPI (Python)
*   **SQL Database**: MySQL with SQLAlchemy ORM
*   **NoSQL Database**: MongoDB with Motor (for AI memory)
*   **AI Engine**: Groq Cloud API
*   **Security**: JWT (jose), Bcrypt (passlib)
*   **Environment**: Dotenv for secure configuration

## 📋 API Endpoints

### Authentication & Profiles
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/students/register` | Create a new student account |
| POST | `/students/login` | Student login to receive JWT |
| GET | `/students/details` | View own student profile (Protected) |
| POST | `/admins/register` | Create a new admin account |
| POST | `/admins/login` | Admin login to receive JWT |

### Admin Operations (Role: Admin Only)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/admin/students` | List all registered students |
| PUT | `/admin/update-marks/{id}` | Update a student's academic marks |
| PUT | `/admin/update-attendance/{id}` | Update attendance percentage |
| POST | `/admin/add-student` | Manually add a new student |

### Academic & General
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/courses` | List all available courses |
| POST | `/courses` | Register a new course (Admin) |
| POST | `/leaves/apply` | Submit a leave application |
| **POST** | **`/chat`** | **AI Assistant (Supports memory & role-context)** |

## ⚙️ Setup & Installation

### 1. Environment Configuration
Create a `.env` file in the root directory:
```bash
DATABASE_URL=mysql+pymysql://user:pass@localhost/campus_ai
JWT_SECRET=your_jwt_secret_key
GROQ_API_KEY=your_groq_api_key
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB=campus_ai_chat
```

### 2. Installations
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
Run the provided SQL script to set up your MySQL schema:
```sql
SOURCE init_db.sql;
```

### 4. Running the Project
```powershell
python main.py
```

## 📖 Documentation
Once the server is running, access the interactive API documentation at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---
*Developed with focus on stability and scalability.*
