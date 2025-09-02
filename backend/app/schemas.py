from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import Optional, Any
from .models import DomainEnum

# Authentication schemas
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None

class UserRead(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Log entry schemas
class LogEntryCreate(BaseModel):
    date: date
    domain: DomainEnum
    metric: str
    value: float
    notes: Optional[str] = None

class LogEntryRead(BaseModel):
    id: str
    user_id: str
    date: date
    domain: DomainEnum
    metric: str
    value: float
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# Journal entry schema (same as LogEntry but with domain=reflection)
class JournalEntryCreate(BaseModel):
    date: date
    content: str
    mood_score: Optional[float] = Field(None, ge=0, le=10)

class JournalEntryRead(BaseModel):
    id: str
    user_id: str
    date: date
    domain: DomainEnum = DomainEnum.reflection
    metric: str = "journal_entry"
    value: float
    notes: str
    
    class Config:
        from_attributes = True

# Correlation insight schemas
class CorrelationInsightRead(BaseModel):
    id: str
    user_id: str
    description: str
    correlation_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Journal summary schemas
class JournalSummaryRead(BaseModel):
    id: str
    user_id: str
    date: date
    summary_text: str
    
    class Config:
        from_attributes = True

class JournalSummaryCreate(BaseModel):
    date: date
    text: str

class AIInsightsResponse(BaseModel):
    insights: str

# Legacy schemas for backward compatibility
class LogCreate(BaseModel):
    user_id: str
    log_date: date
    domain: str
    value: Optional[float] = None
    metrics: Optional[dict[str, Any]] = None
    note: Optional[str] = None

class LogRead(LogCreate):
    id: str
    class Config:
        from_attributes = True

class InsightRead(BaseModel):
    id: str
    user_id: str
    week_start: date
    summary: Optional[str] = None
    correlations: Optional[dict[str, Any]] = None
    class Config:
        from_attributes = True

class InsightUpsert(BaseModel):
    user_id: str
    week_start: date
    summary: Optional[str] = None
    correlations: Optional[dict[str, Any]] = None 