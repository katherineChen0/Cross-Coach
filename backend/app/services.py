from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import User, LogEntry, CorrelationInsight, DomainEnum
from .schemas import UserRegister, LogEntryCreate, JournalEntryCreate
from .core.auth import get_password_hash, verify_password
from datetime import date
import uuid


def create_user(db: Session, payload: UserRegister) -> User:
    """Create a new user with hashed password."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise ValueError("User with this email already exists")
    
    hashed_password = get_password_hash(payload.password)
    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Authenticate a user with email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_user(db: Session, user_id: str) -> User | None:
    """Get user by ID."""
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_log_entry(db: Session, user_id: str, payload: LogEntryCreate) -> LogEntry:
    """Create a new log entry."""
    log_entry = LogEntry(
        user_id=user_id,
        date=payload.date,
        domain=payload.domain,
        metric=payload.metric,
        value=payload.value,
        notes=payload.notes
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def create_journal_entry(db: Session, user_id: str, payload: JournalEntryCreate) -> LogEntry:
    """Create a journal entry (stored as LogEntry with domain=reflection)."""
    # Use mood_score as value if provided, otherwise use 0
    value = payload.mood_score if payload.mood_score is not None else 0.0
    
    journal_entry = LogEntry(
        user_id=user_id,
        date=payload.date,
        domain=DomainEnum.reflection,
        metric="journal_entry",
        value=value,
        notes=payload.content
    )
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    return journal_entry


def get_logs_for_user(db: Session, user_id: str) -> list[LogEntry]:
    """Get all log entries for a user."""
    stmt = select(LogEntry).where(LogEntry.user_id == user_id).order_by(LogEntry.date.desc())
    return list(db.execute(stmt).scalars().all())


def get_correlation_insights_for_user(db: Session, user_id: str) -> list[CorrelationInsight]:
    """Get correlation insights for a user."""
    stmt = select(CorrelationInsight).where(CorrelationInsight.user_id == user_id).order_by(CorrelationInsight.created_at.desc())
    return list(db.execute(stmt).scalars().all())


# Legacy functions for backward compatibility
def create_log(db: Session, payload) -> LogEntry:
    """Legacy function for backward compatibility."""
    log_entry = LogEntry(
        user_id=payload.user_id,
        date=payload.log_date,
        domain=payload.domain,
        metric="legacy_metric",
        value=payload.value or 0.0,
        notes=payload.note
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry 