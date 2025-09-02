from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import User, LogEntry, CorrelationInsight, JournalSummary, DomainEnum
from .schemas import UserRegister, LogEntryCreate, JournalEntryCreate
from .core.auth import get_password_hash, verify_password
from .core.config import settings
from datetime import date
import uuid
import openai


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


def summarize_journal(text: str) -> str:
    """
    Use OpenAI GPT API to summarize journal text into 2-3 sentences.
    
    Args:
        text: The journal text to summarize
        
    Returns:
        A 2-3 sentence summary of the journal entry
    """
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key not configured")
    
    # Configure OpenAI client
    client = openai.OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base
    )
    
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes journal entries. Provide concise, 2-3 sentence summaries that capture the key themes, emotions, and insights from the journal entry. Focus on the most important points and maintain a supportive, understanding tone."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this journal entry in 2-3 sentences:\n\n{text}"
                }
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback to a simple summary if API call fails
        words = text.split()
        if len(words) <= 20:
            return text
        else:
            return " ".join(words[:20]) + "..."


def create_journal_summary(db: Session, user_id: str, date: date, text: str) -> JournalSummary:
    """
    Create a journal summary and store it in the database.
    
    Args:
        db: Database session
        user_id: User ID
        date: Date of the journal entry
        text: Journal text to summarize
        
    Returns:
        The created JournalSummary object
    """
    summary_text = summarize_journal(text)
    
    journal_summary = JournalSummary(
        user_id=user_id,
        date=date,
        summary_text=summary_text
    )
    
    db.add(journal_summary)
    db.commit()
    db.refresh(journal_summary)
    return journal_summary


def generate_ai_coach_insights(logs: list[LogEntry], correlations: list[CorrelationInsight]) -> str:
    """
    Generate AI coach insights based on user data and correlations.
    
    Args:
        logs: List of user's log entries
        correlations: List of correlation insights
        
    Returns:
        A string containing 1-2 weekly recommendations in natural language
    """
    if not settings.openai_api_key:
        return "AI insights not available - OpenAI API key not configured."
    
    # Prepare data for analysis
    recent_logs = sorted(logs, key=lambda x: x.date, reverse=True)[:50]  # Last 50 entries
    
    # Create a summary of recent activity
    activity_summary = []
    for log in recent_logs:
        activity_summary.append(f"{log.date}: {log.domain.value} - {log.metric}: {log.value}")
        if log.notes:
            activity_summary.append(f"  Notes: {log.notes}")
    
    # Prepare correlation insights
    correlation_text = ""
    if correlations:
        correlation_text = "Recent insights about your patterns:\n"
        for corr in correlations[:5]:  # Top 5 correlations
            correlation_text += f"- {corr.description} (correlation: {corr.correlation_score:.2f})\n"
    
    # Configure OpenAI client
    client = openai.OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base
    )
    
    try:
        prompt = f"""
You are an AI coach analyzing a user's wellness data. Based on their recent activity and patterns, provide 1-2 specific, actionable weekly recommendations.

Recent Activity:
{chr(10).join(activity_summary[:20])}  # Limit to first 20 entries for brevity

{correlation_text}

Please provide 1-2 specific, actionable recommendations for the upcoming week. Focus on:
- Building on positive patterns
- Addressing areas for improvement
- Specific, measurable actions
- Supportive and encouraging tone

Format your response as natural, conversational advice (2-3 sentences per recommendation).
"""
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a supportive AI wellness coach. Provide specific, actionable advice based on user data patterns. Be encouraging and practical."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.4
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Unable to generate AI insights at this time. Error: {str(e)}"


def get_journal_summaries_for_user(db: Session, user_id: str) -> list[JournalSummary]:
    """Get journal summaries for a user."""
    stmt = select(JournalSummary).where(JournalSummary.user_id == user_id).order_by(JournalSummary.date.desc())
    return list(db.execute(stmt).scalars().all()) 