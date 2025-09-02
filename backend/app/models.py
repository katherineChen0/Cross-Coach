from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Date, Float, ForeignKey, func, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

class Base(DeclarativeBase):
    pass

class DomainEnum(enum.Enum):
    fitness = "fitness"
    climbing = "climbing"
    learning = "learning"
    reflection = "reflection"
    sleep = "sleep"
    other = "other"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    # Relationships
    log_entries: Mapped[list["LogEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    correlation_insights: Mapped[list["CorrelationInsight"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    journal_summaries: Mapped[list["JournalSummary"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    domain: Mapped[DomainEnum] = mapped_column(Enum(DomainEnum), nullable=False)
    metric: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped[User] = relationship(back_populates="log_entries")

    # Indexes for performance
    __table_args__ = (
        Index('idx_log_entries_user_date', 'user_id', 'date'),
    )

class CorrelationInsight(Base):
    __tablename__ = "correlation_insights"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    # Relationships
    user: Mapped[User] = relationship(back_populates="correlation_insights")

class JournalSummary(Base):
    __tablename__ = "journal_summaries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="journal_summaries")

    # Indexes for performance
    __table_args__ = (
        Index('idx_journal_summaries_user_date', 'user_id', 'date'),
    ) 