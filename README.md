# LC Management System

> A comprehensive FastAPI-based backend for educational institutions with monthly payment system, student management, and debt tracking.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat&logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg?style=flat&logo=postgresql)](https://postgresql.org)
[![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E.svg?style=flat&logo=railway)](https://railway.app)

## 🚀 Features

- 🔐 **JWT Authentication** with role-based permissions (Teacher, Admin, Superadmin)
- 💰 **Monthly Payment System** with automatic debt calculation and tracking
- 👥 **Student Management** with multi-course enrollment support
- 📚 **Course Management** with scheduling and pricing
- 📊 **Attendance Tracking** with lesson counting per course
- 📈 **Comprehensive Reporting** and statistics
- 🌐 **RESTful API** with OpenAPI/Swagger documentation
- 🎯 **Production Ready** with Railway deployment and auto-initialization

## 📖 Documentation

- **[Complete Documentation](COMPLETE_DOCUMENTATION.md)** - Full API reference, usage examples, and guides
- **[Technical Architecture](TECHNICAL_ARCHITECTURE.md)** - System design, database schema, and architecture details
- **[Interactive API Docs](https://your-railway-url.com/docs)** - Live API testing interface

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/umaraliyev0101/Averna_LC.git
cd Averna_LC

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Create .env file
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./education_management.db
CORS_ORIGINS=*
```

### 3. Start Application
```bash
python start.py
```

### 4. Access API
- 🌐 **API Base**: http://localhost:8000
- 📚 **Documentation**: http://localhost:8000/docs
- 💓 **Health Check**: http://localhost:8000/health

## 🔑 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin` | Administrator |
| `superadmin` | `super` | Super Administrator |
| `teacher1` | `teach` | Teacher |

## 💰 Monthly Payment System

The core feature of this system - automatic monthly billing and debt tracking:

```python
# Example: Student enrolled in English course for 2 months
Course: "English Language" - 150,000 UZS/month
Enrollment: September 1, 2024 (2 months ago)
Total Owed: 150,000 × 2 = 300,000 UZS
Total Paid: 250,000 UZS
Balance: -50,000 UZS (Student owes 50,000 UZS)
```

### Key Endpoints
- `GET /debt/student/{id}/monthly-debt` - Calculate student debt
- `POST /debt/student/{id}/enroll-course` - Enroll in course (starts billing)
- `POST /debt/student/{id}/payment` - Record payment
- `GET /debt/monthly-summary` - All students debt overview

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   PostgreSQL    │
│   (Telegram     │◄──►│   Backend        │◄──►│   Database      │
│   Bot/Mobile)   │    │   (This System)  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Technology Stack
- **Backend**: FastAPI 0.115.6, Python 3.11+
- **Database**: PostgreSQL (Production), SQLite (Development)  
- **ORM**: SQLAlchemy 2.0.36 with automatic migrations
- **Auth**: JWT tokens with SHA256+salt password hashing
- **Validation**: Pydantic 2.10.3 with comprehensive type checking
- **Deployment**: Railway cloud platform with auto-deployment

## 📊 Core API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User authentication |
| `/students/` | GET/POST | Student management |
| `/courses/` | GET/POST | Course management |
| `/payments/` | GET/POST | Payment processing |
| `/debt/monthly-summary` | GET | Debt overview |
| `/stats/overview` | GET | System statistics |

## 🚀 Deployment

### Railway (Production)
Automatically deployed on Railway with:
- ✅ PostgreSQL database integration  
- ✅ Auto-initialization with sample data
- ✅ Environment variable configuration
- ✅ SSL/HTTPS enabled
- ✅ Custom domain support

### Docker (Alternative)
```bash
docker build -t lc-management .
docker run -p 8000:8000 lc-management
```

## 🔧 Development

### Project Structure
```
app/
├── main.py              # FastAPI application entry
├── models/              # Database models
├── schemas/             # Pydantic validation schemas  
├── api/                 # Route handlers
│   ├── auth.py          # Authentication
│   ├── debt.py          # Monthly payment system ⭐
│   ├── students.py      # Student management
│   └── ...
├── core/                # Core functionality
└── crud/                # Database operations
```

### Key Features Implementation
- **Monthly Billing**: `StudentCourseProgress` model tracks enrollment dates
- **Debt Calculation**: Automatic calculation based on enrollment duration
- **Multi-Course Support**: Students can enroll in multiple courses simultaneously
- **Role-Based Access**: Teachers, Admins, and Superadmins with different permissions

## 📈 Usage Example

```python
# 1. Login and get token
POST /auth/login
{"username": "admin", "password": "admin"}

# 2. Create student
POST /students/
{"name": "John", "surname": "Doe", ...}

# 3. Enroll in course (starts monthly billing)
POST /debt/student/1/enroll-course
{"course_id": 1, "enrollment_date": "2025-10-07"}

# 4. Record payment
POST /debt/student/1/payment  
{"course_id": 1, "amount": 150.0, "description": "October payment"}

# 5. Check debt status
GET /debt/student/1/monthly-debt
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 **Full Documentation**: [COMPLETE_DOCUMENTATION.md](COMPLETE_DOCUMENTATION.md)
- 🏗️ **Architecture Guide**: [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/umaraliyev0101/Averna_LC/issues)
- 🧪 **API Testing**: Interactive docs at `/docs` endpoint

---
*Built with ❤️ for educational institutions. Ready for production use.*
