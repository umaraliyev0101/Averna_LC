# Education Management API Documentation

## Base URL
```
http://localhost:8001
```

## Authentication Method

The API uses JWT (JSON Web Token) authentication for secure access:

### JWT Token Authentication
- **Login:** `POST /auth/login`
- **Usage:** Include token in `Authorization: Bearer <token>` header
- **Security:** Industry standard, tokens expire after 30 minutes
- **Best for:** All applications (web, mobile, desktop)

---

## Authentication Endpoints

### Login (JWT Token)
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Invalid credentials
- `422`: Validation error

---

## User Management

### Get Current User Info
```http
GET /users/me
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "role": "admin"
}
```

### Get All Users (Admin Only)
```http
GET /users/
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "role": "admin"
  },
  {
    "id": 2,
    "username": "teacher1",
    "role": "teacher"
  }
]
```

---

## Students Management

### Get All Students
```http
GET /students/
Authorization: Bearer <token>
```

**Required Role:** Admin, Superadmin

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "John",
    "surname": "Doe",
    "second_name": "Michael",
    "starting_date": "2024-01-15",
    "num_lesson": 8,
    "total_money": 1200.0,
    "courses": [1, 3],
    "attendance": [
      {
        "date": "2024-01-15",
        "isAbsent": false,
        "reason": ""
      }
    ]
  }
]
```

### Get Student by ID
```http
GET /students/{student_id}
Authorization: Bearer <token>
```

**Response (200):** Same as single student object above

**Errors:**
- `404`: Student not found
- `403`: Insufficient permissions

### Create Student
```http
POST /students/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "surname": "string",
  "second_name": "string",
  "starting_date": "2024-01-15",
  "num_lesson": 0,
  "total_money": 0.0,
  "courses": [1, 2]
}
```

**Required Role:** Admin, Superadmin

**Response (201):** Created student object

### Update Student
```http
PUT /students/{student_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "surname": "string",
  "second_name": "string",
  "starting_date": "2024-01-15",
  "num_lesson": 10,
  "total_money": 1500.0,
  "courses": [1, 2, 3]
}
```

**Required Role:** Admin, Superadmin

### Delete Student
```http
DELETE /students/{student_id}
Authorization: Bearer <token>
```

**Required Role:** Admin, Superadmin

**Response (200):**
```json
{
  "message": "Student deleted successfully"
}
```

---

## Courses Management

### Get All Courses
```http
GET /courses/
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "English Language",
    "week_days": ["Monday", "Wednesday", "Friday"],
    "lesson_per_month": 12,
    "cost": 150.0
  }
]
```

### Get Course by ID
```http
GET /courses/{course_id}
Authorization: Bearer <token>
```

### Create Course
```http
POST /courses/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "week_days": ["Monday", "Wednesday"],
  "lesson_per_month": 8,
  "cost": 120.0
}
```

**Required Role:** Admin, Superadmin

### Update Course
```http
PUT /courses/{course_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "week_days": ["Tuesday", "Thursday"],
  "lesson_per_month": 10,
  "cost": 150.0
}
```

### Delete Course
```http
DELETE /courses/{course_id}
Authorization: Bearer <token>
```

**Required Role:** Admin, Superadmin

---

## Attendance Management

### Record Attendance
```http
POST /attendance/
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": 1,
  "date": "2024-01-15",
  "isAbsent": false,
  "reason": "Present"
}
```

**Required Role:** Teacher, Admin, Superadmin

**Response (200):**
```json
{
  "message": "Attendance recorded successfully",
  "student_id": 1,
  "date": "2024-01-15",
  "isAbsent": false
}
```

### Get Student Attendance
```http
GET /attendance/{student_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "student_id": 1,
  "student_name": "John Doe",
  "attendance": [
    {
      "date": "2024-01-15",
      "isAbsent": false,
      "reason": ""
    }
  ]
}
```

---

## Payments Management

### Get All Payments
```http
GET /payments/
Authorization: Bearer <token>
```

**Required Role:** Admin, Superadmin

**Response (200):**
```json
[
  {
    "id": 1,
    "student_id": 1,
    "amount": 150.0,
    "payment_date": "2024-01-15",
    "payment_method": "cash",
    "description": "Monthly payment"
  }
]
```

### Record Payment
```http
POST /payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": 1,
  "amount": 150.0,
  "payment_date": "2024-01-15",
  "payment_method": "cash",
  "description": "Monthly payment"
}
```

---

## Statistics

### Get System Statistics
```http
GET /stats/overview
Authorization: Bearer <token>
```

**Required Role:** Admin, Superadmin

**Response (200):**
```json
{
  "total_students": 25,
  "total_courses": 8,
  "total_teachers": 5,
  "monthly_revenue": 15000.0,
  "attendance_rate": 85.5
}
```



---

## Error Handling

### Standard HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Validation Error Response
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## User Roles and Permissions

### Role Hierarchy
1. **Superadmin**: Full access to all endpoints
2. **Admin**: Access to most endpoints, cannot manage superadmins
3. **Teacher**: Limited access, mainly attendance and viewing

### Permission Matrix

| Endpoint | Teacher | Admin | Superadmin |
|----------|---------|-------|------------|
| View Students | ❌ | ✅ | ✅ |
| Create/Edit Students | ❌ | ✅ | ✅ |
| View Courses | ✅ | ✅ | ✅ |
| Create/Edit Courses | ❌ | ✅ | ✅ |
| Record Attendance | ✅ | ✅ | ✅ |
| View Payments | ❌ | ✅ | ✅ |
| Create Payments | ❌ | ✅ | ✅ |
| View Statistics | ❌ | ✅ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |

---

## Frontend Integration Examples

### JavaScript/React Example

```javascript
class EducationAPI {
  constructor(baseURL = 'http://localhost:8001') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('auth_token', this.token);
      return data;
    }
    throw new Error('Login failed');
  }

  async getStudents() {
    const response = await fetch(`${this.baseURL}/students/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch students');
  }

  async recordAttendance(studentId, date, isAbsent, reason = '') {
    const response = await fetch(`${this.baseURL}/attendance/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
      body: JSON.stringify({
        student_id: studentId,
        date: date,
        isAbsent: isAbsent,
        reason: reason,
      }),
    });

    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to record attendance');
  }
}

// Usage
const api = new EducationAPI();

// Login
await api.login('admin', 'admin123');

// Get students
const students = await api.getStudents();

// Record attendance
await api.recordAttendance(1, '2024-01-15', false, 'Present');
```

### Python Requests Example

```python
import requests
from datetime import date

class EducationAPI:
    def __init__(self, base_url='http://localhost:8001'):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        response = requests.post(f'{self.base_url}/auth/login', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            return data
        raise Exception('Login failed')

    def get_headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def get_students(self):
        response = requests.get(
            f'{self.base_url}/students/', 
            headers=self.get_headers()
        )
        return response.json()

    def record_attendance(self, student_id, date, is_absent, reason=''):
        response = requests.post(
            f'{self.base_url}/attendance/',
            json={
                'student_id': student_id,
                'date': date.isoformat(),
                'isAbsent': is_absent,
                'reason': reason
            },
            headers=self.get_headers()
        )
        return response.json()

# Usage
api = EducationAPI()
api.login('admin', 'admin123')
students = api.get_students()
api.record_attendance(1, date.today(), False, 'Present')
```

---

## Testing the API

### Using cURL

```bash
# Login
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token (replace TOKEN with actual token)
curl -X GET "http://localhost:8001/students/" \
  -H "Authorization: Bearer TOKEN"

# Direct auth (no token needed)
curl -X POST "http://localhost:8001/direct/students" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Interactive API Documentation

Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## Rate Limiting and Best Practices

### Recommendations
1. **Cache tokens**: Store JWT tokens securely and reuse them
2. **Handle errors gracefully**: Always check response status codes
3. **Use HTTPS in production**: Never send credentials over HTTP
4. **Implement retry logic**: Handle temporary network failures
5. **Validate input**: Check data before sending to API

### Security Notes
- JWT tokens expire after 30 minutes
- Always use HTTPS in production
- Store tokens securely (not in localStorage for sensitive apps)
- Implement proper error handling for authentication failures

---

## Contact and Support

- **API Version**: 1.0.0
- **Server Status**: `/health` endpoint
- **Documentation**: `/docs` (Swagger UI)
