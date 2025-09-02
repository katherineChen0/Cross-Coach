from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from .. import services
from ..core.auth import get_current_user, create_access_token
from ..models import User
from ..schemas import (
    UserRegister, UserLogin, Token, UserRead,
    LogEntryCreate, LogEntryRead, JournalEntryCreate, JournalEntryRead,
    CorrelationInsightRead
)

api_router = APIRouter()

# Authentication routes
@api_router.post("/register", response_model=UserRead)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        user = services.create_user(db, payload)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = services.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected routes (require authentication)
@api_router.post("/log", response_model=LogEntryRead)
def add_log_entry(
    payload: LogEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a log entry for the current user."""
    log_entry = services.create_log_entry(db, str(current_user.id), payload)
    return log_entry

@api_router.get("/logs", response_model=list[LogEntryRead])
def get_user_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all log entries for the current user."""
    return services.get_logs_for_user(db, str(current_user.id))

@api_router.post("/journal", response_model=JournalEntryRead)
def submit_journal_entry(
    payload: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a journal entry (stored as LogEntry with domain=reflection)."""
    journal_entry = services.create_journal_entry(db, str(current_user.id), payload)
    return journal_entry

@api_router.get("/insights", response_model=list[CorrelationInsightRead])
def get_user_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get correlation insights for the current user."""
    return services.get_correlation_insights_for_user(db, str(current_user.id))

# Legacy routes for backward compatibility
@api_router.post("/users", response_model=UserRead)
def create_user(payload, db: Session = Depends(get_db)):
    user = services.create_user(db, payload)
    return user

@api_router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = services.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.post("/logs", response_model=LogEntryRead)
def create_log(payload, db: Session = Depends(get_db)):
    return services.create_log(db, payload)

@api_router.get("/logs/{user_id}", response_model=list[LogEntryRead])
def get_logs(user_id: str, db: Session = Depends(get_db)):
    return services.get_logs_for_user(db, user_id) 