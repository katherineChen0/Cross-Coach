from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
	from sqlalchemy.orm import Session
	try:
		db: Session = SessionLocal()
		yield db
	finally:
		db.close() 