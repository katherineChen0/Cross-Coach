# Cross-Coach Database Setup

This document describes the database schema and setup for the Cross-Coach application.

## Database Schema

The application uses PostgreSQL with the following tables:

### Users Table
- `id`: UUID primary key
- `name`: User's full name
- `email`: Unique email address
- `password_hash`: Hashed password for authentication
- `created_at`: Timestamp when user was created

### LogEntry Table
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `date`: Date of the log entry
- `domain`: Enum with values: fitness, climbing, learning, reflection, sleep, other
- `metric`: String describing what was measured
- `value`: Float value of the measurement
- `notes`: Optional text notes

### CorrelationInsight Table
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `description`: Text description of the correlation insight
- `correlation_score`: Float representing the correlation strength
- `created_at`: Timestamp when insight was created

### JournalSummary Table
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `date`: Date of the journal summary
- `summary_text`: Text content of the journal summary

## Performance Indexes

The following indexes are created for optimal performance:

- `idx_log_entries_user_date`: Composite index on (user_id, date) for LogEntry
- `idx_journal_summaries_user_date`: Composite index on (user_id, date) for JournalSummary
- `idx_log_entries_domain`: Index on domain for filtering
- `idx_log_entries_date`: Index on date for date-based queries
- `idx_correlation_insights_user_id`: Index on user_id for CorrelationInsight
- `idx_correlation_insights_created_at`: Index on created_at for sorting

## Setup Instructions

### 1. Using Docker Compose (Recommended)

The project includes a `docker-compose.yml` file that sets up PostgreSQL automatically:

```bash
# Start the database
docker-compose up -d db

# Run migrations
cd backend
alembic upgrade head
```

### 2. Manual PostgreSQL Setup

If you prefer to set up PostgreSQL manually:

1. Install PostgreSQL
2. Create a database named `crosscoach`
3. Create a user with appropriate permissions
4. Update the `DATABASE_URL` in your environment variables
5. Run the schema creation:

```bash
# Option A: Use the SQL schema file
psql -d crosscoach -f db/schema.sql

# Option B: Use Alembic migrations
cd backend
alembic upgrade head
```

### 3. Environment Variables

Set the following environment variables:

```bash
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/crosscoach
```

## Database Migrations

The project uses Alembic for database migrations:

### Initialize Alembic (first time only)
```bash
cd backend
alembic init alembic
```

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1  # Go back one revision
alembic downgrade base  # Go back to beginning
```

## Usage Examples

### Creating a User
```python
from app.models import User
from app.db import get_db

db = next(get_db())
user = User(
    name="John Doe",
    email="john@example.com",
    password_hash="hashed_password_here"
)
db.add(user)
db.commit()
```

### Adding a Log Entry
```python
from app.models import LogEntry, DomainEnum
from datetime import date

log_entry = LogEntry(
    user_id=user.id,
    date=date.today(),
    domain=DomainEnum.fitness,
    metric="weight",
    value=75.5,
    notes="Morning weight after workout"
)
db.add(log_entry)
db.commit()
```

### Querying Log Entries
```python
# Get all log entries for a user in a date range
from datetime import date, timedelta

start_date = date.today() - timedelta(days=7)
end_date = date.today()

entries = db.query(LogEntry).filter(
    LogEntry.user_id == user.id,
    LogEntry.date >= start_date,
    LogEntry.date <= end_date
).all()
```

## Data Types and Constraints

- **UUIDs**: All primary keys use UUID type for better distribution and security
- **Foreign Keys**: All foreign keys have CASCADE delete for data integrity
- **Enums**: Domain field uses PostgreSQL enum for data validation
- **Indexes**: Composite indexes on (user_id, date) for efficient queries
- **Timestamps**: Automatic timestamp creation for audit trails

## Backup and Recovery

### Create a backup
```bash
pg_dump -h localhost -U username -d crosscoach > backup.sql
```

### Restore from backup
```bash
psql -h localhost -U username -d crosscoach < backup.sql
``` 