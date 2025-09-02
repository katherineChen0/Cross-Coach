# CrossCoach API Documentation

## Overview

The CrossCoach API provides endpoints for user registration, authentication, logging activities, journaling, and correlation insights. The API uses JWT authentication for secure access to protected endpoints.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication Endpoints

#### POST /api/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

#### POST /api/login
Login and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Protected Endpoints (Require Authentication)

#### POST /api/log
Add a log entry for the current user.

**Request Body:**
```json
{
  "date": "2024-01-15",
  "domain": "fitness",
  "metric": "workout_duration",
  "value": 45.0,
  "notes": "Morning workout session"
}
```

**Available Domains:**
- `fitness` - Physical fitness activities
- `climbing` - Climbing activities
- `learning` - Learning and education
- `reflection` - Journal entries and reflections
- `sleep` - Sleep tracking
- `other` - Other activities

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "date": "2024-01-15",
  "domain": "fitness",
  "metric": "workout_duration",
  "value": 45.0,
  "notes": "Morning workout session"
}
```

#### GET /api/logs
Get all log entries for the current user.

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "date": "2024-01-15",
    "domain": "fitness",
    "metric": "workout_duration",
    "value": 45.0,
    "notes": "Morning workout session"
  }
]
```

#### POST /api/journal
Submit a journal entry (stored as LogEntry with domain=reflection).

**Request Body:**
```json
{
  "date": "2024-01-15",
  "content": "Today was a great day! I felt energized and productive.",
  "mood_score": 8.5
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "date": "2024-01-15",
  "domain": "reflection",
  "metric": "journal_entry",
  "value": 8.5,
  "notes": "Today was a great day! I felt energized and productive."
}
```

#### GET /api/insights
Get correlation insights for the current user.

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "description": "Strong positive correlation (0.85) between Fitness Workout Duration and Sleep Hours",
    "correlation_score": 0.85,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

## Background Analytics Service

The API includes a background analytics service that runs weekly (every Sunday at 2 AM) to compute correlations between different user metrics using Pearson correlation coefficients.

### Features:
- **Automatic Analysis**: Runs weekly without user intervention
- **Statistical Significance**: Only includes correlations with p < 0.05
- **Minimum Strength**: Only includes correlations with |r| > 0.3
- **Data Requirements**: Requires at least 5 data points for each correlation
- **Multi-metric Analysis**: Compares all available metrics for each user

### Correlation Insights:
- **Strong Correlation**: |r| > 0.7
- **Moderate Correlation**: 0.5 < |r| ≤ 0.7
- **Weak Correlation**: 0.3 < |r| ≤ 0.5

## Error Responses

### 400 Bad Request
```json
{
  "detail": "User with this email already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (see `.env.example`)

3. Run the API:
```bash
uvicorn app.main:app --reload
```

4. Test the API:
```bash
python test_api.py
```

## Database Schema

The API uses the following main models:

- **User**: User accounts with email, name, and hashed password
- **LogEntry**: Activity logs with domain, metric, value, and notes
- **CorrelationInsight**: Computed correlations between user metrics

## Security Features

- **Password Hashing**: Passwords are hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configurable CORS settings
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries 