# 🤝 Frontend Integration Guide

This guide explains how to connect your frontend application to the LC Management API over LAN.

## 🚀 Starting the API Server

### Option 1: Quick Start (Recommended)
```bash
cd "d:\Projects\LC management"
.\venv\Scripts\Activate.ps1
python start_lan_server.py
```

### Option 2: Manual Start
```bash
cd "d:\Projects\LC management"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📡 API Connection Details

When the server starts, you'll see output like:
```
📡 Local access: http://127.0.0.1:8001
🌐 LAN access: http://192.168.1.100:8001
📚 API docs: http://192.168.1.100:8001/docs
```

**Share these URLs with your frontend developer:**
- **Base API URL**: `http://[YOUR_IP]:8001`
- **Login Endpoint**: `http://[YOUR_IP]:8001/auth/login`
- **API Documentation**: `http://[YOUR_IP]:8001/docs`

## 🔐 Authentication Flow

### 1. Login Request
```javascript
// POST /auth/login
const loginResponse = await fetch('http://[YOUR_IP]:8001/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const data = await loginResponse.json();
// Response: { access_token, token_type, user_id, username, role }
```

### 2. Using the Token
```javascript
// Include in all subsequent requests
const token = data.access_token;

const response = await fetch('http://[YOUR_IP]:8001/students/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## 📋 Available Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token

### Students
- `GET /students/` - List all students
- `POST /students/` - Create new student
- `GET /students/{id}` - Get student by ID
- `PUT /students/{id}` - Update student
- `DELETE /students/{id}` - Delete student

### Courses
- `GET /courses/` - List all courses
- `POST /courses/` - Create new course
- `GET /courses/{id}` - Get course by ID
- `PUT /courses/{id}` - Update course
- `DELETE /courses/{id}` - Delete course

### Payments
- `GET /payments/` - List payments (with filters)
- `POST /payments/` - Create new payment
- `GET /payments/{id}` - Get payment by ID
- `PUT /payments/{id}` - Update payment
- `DELETE /payments/{id}` - Delete payment

### Attendance
- `POST /attendance/check` - Record attendance
- `GET /attendance/student/{student_id}` - Get student attendance

### Statistics
- `GET /stats/` - General statistics
- `GET /stats/by-course` - Payment stats by course
- `GET /stats/monthly/{year}` - Monthly statistics

### Users (Admin/Superadmin only)
- `GET /users/` - List all users
- `POST /users/` - Create new user
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## 🧪 Test Users

| Username   | Password   | Role       | Permissions |
|------------|------------|------------|-------------|
| admin      | admin123   | admin      | Students, Courses, Payments, Attendance |
| teacher1   | teacher123 | teacher    | Attendance only |
| superadmin | super123   | superadmin | All permissions + User management |

## 🌐 Network Configuration

### Windows Firewall
If your friend can't connect, you may need to allow the port:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → "TCP" → "Specific local ports: 8001"
5. Allow the connection

### Router Configuration
If on different subnets, ensure your router allows communication between devices.

## 🔍 Troubleshooting

### Connection Issues
1. **Check if server is running**: Visit `http://[YOUR_IP]:8001/health`
2. **Firewall**: Ensure port 8001 is open
3. **Network**: Ensure both devices are on same network
4. **IP address**: Use `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to verify IP

### CORS Issues
The API is configured to allow all origins during development. If you encounter CORS issues:
- Check browser console for specific error messages
- Ensure you're using the correct IP address
- Try accessing the API docs at `http://[YOUR_IP]:8001/docs`

## 📱 Frontend Examples

### React/JavaScript
```javascript
const API_BASE = 'http://192.168.1.100:8001';

// Login
const login = async (username, password) => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return response.json();
};

// Get students
const getStudents = async (token) => {
  const response = await fetch(`${API_BASE}/students/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### Axios (Recommended)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.1.100:8001',
});

// Add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## 📚 Interactive API Documentation

Visit `http://[YOUR_IP]:8001/docs` to:
- See all available endpoints
- Test API calls directly in browser
- View request/response schemas
- Understand authentication requirements

## 🔒 Security Notes

- This configuration is for **development only**
- Change CORS settings for production
- Use HTTPS in production
- Store tokens securely (not in localStorage for production)
- Implement proper error handling

## 📞 Support

If your frontend developer encounters issues:
1. Check the server logs in your terminal
2. Test endpoints using the API docs at `/docs`
3. Verify network connectivity with ping/curl
4. Check firewall settings on both machines
