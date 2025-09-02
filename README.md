# Cross-Coach

A comprehensive fitness and wellness tracking application with AI-powered insights and analytics.

## 🚀 Quick Start with Docker Compose

This setup includes:
- **PostgreSQL Database** - Data persistence
- **FastAPI Backend** - REST API with AI analytics
- **React Frontend** - Modern web interface served with nginx
- **Seed Data** - Pre-populated with example user and 2 weeks of realistic data

### Prerequisites

- Docker and Docker Compose installed
- Optional: OpenAI API key for AI insights

### 1. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` to add your OpenAI API key (optional):
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Start the Application

```bash
docker-compose up -d
```

This will start all services:
- Database: `localhost:5432`
- Backend API: `localhost:8000`
- Frontend: `http://localhost:3000`
- Analytics: Running in background

### 3. Seed Data

The application automatically creates:
- **User**: `kath@example.com` / `password123`
- **2 weeks of sample data** including:
  - Sleep hours (4-9 hours)
  - Climbing performance (0-10 scale)
  - Fitness minutes (0-90 minutes)
  - Coding hours (0-8 hours)
  - Mood ratings (1-5 scale)
  - Daily journal entries

### 4. Example User Flow

#### Login
- Email: `kath@example.com`
- Password: `password123`

#### Sample Data Insights

The seed data includes realistic correlations:

1. **Sleep & Climbing Performance**
   - Climbing sessions are 25% better after 7+ hours of sleep
   - Data shows improved grades on well-rested days

2. **Coding & Mood Correlation**
   - Mood dips on days with >3h coding but no exercise
   - Exercise helps balance long coding sessions

3. **Sleep Quality Impact**
   - Overall performance improves with better sleep
   - Consistent 7+ hour sleep nights show better metrics

### 5. Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (user: crosscoach, db: crosscoach)

### 6. Services Overview

#### Database (PostgreSQL)
- Stores user data, logs, and insights
- Automatic initialization with schema
- Persistent data storage

#### Backend (FastAPI)
- RESTful API endpoints
- AI-powered analytics
- User authentication
- Data processing and insights

#### Frontend (React + Nginx)
- Modern React application
- Served by nginx for production
- API proxy configuration
- Optimized static file serving

#### Analytics Service
- Background processing
- Correlation analysis
- AI insight generation
- Runs after seed data is loaded

### 7. Development

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

#### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

#### Rebuild and Restart
```bash
# Rebuild all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

#### Reset Data
```bash
# Stop and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d
```

### 8. Seed Data Details

The seed script creates realistic data patterns:

#### Sleep Data
- Range: 4-9 hours
- 40% chance of 7+ hours (good sleep)
- Affects climbing performance

#### Climbing Performance
- Base range: 3-8 (normalized grade)
- +1-2 points after 7+ hours sleep
- Shows correlation with rest

#### Fitness Activity
- 0-90 minutes per day
- Random distribution
- Affects mood balance

#### Coding Hours
- 0-8 hours per day
- 30% chance of >3 hours
- Can impact mood without exercise

#### Mood Ratings
- 1-5 scale
- Dips when coding >3h without exercise
- Better with good sleep and activity

### 9. Troubleshooting

#### Database Connection Issues
```bash
# Check database status
docker-compose ps db

# View database logs
docker-compose logs db
```

#### Backend Issues
```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
docker-compose logs backend
```

#### Frontend Issues
```bash
# Check frontend build
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

#### Reset Everything
```bash
# Complete reset
docker-compose down -v
docker system prune -f
docker-compose up -d
```

### 10. Production Deployment

For production deployment:

1. Update environment variables
2. Use production database credentials
3. Configure proper CORS origins
4. Set up SSL certificates
5. Use external database if needed

### 11. API Endpoints

Key endpoints available:
- `GET /health` - Service health check
- `POST /api/auth/login` - User authentication
- `GET /api/logs` - Retrieve user logs
- `POST /api/logs` - Create new log entry
- `GET /api/insights` - Get AI-generated insights

Full API documentation available at: http://localhost:8000/docs

---

## 🎯 Example Analytics Insights

After running the analytics service, you should see insights like:

- "Climbing sessions are 25% better after 7+ hours of sleep"
- "Mood dips on days with >3h coding but no exercise"
- "Sleep quality significantly impacts overall performance"
- "Regular exercise helps maintain mood during intensive coding periods"

These insights are generated from the realistic correlations built into the seed data.