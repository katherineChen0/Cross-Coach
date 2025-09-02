from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import SessionLocal
from ..models import User, Log


def ensure_user(db: Session, email: str, name: str) -> User:
	user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
	if user:
		return user
	user = User(email=email, name=name)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def seed_logs(db: Session, user: User):
	end = date.today()
	start = end - timedelta(days=13)
	curr = start
	from random import random
	while curr <= end:
		# Fitness: minutes trained (0-90)
		db.add(Log(user_id=user.id, log_date=curr, domain="fitness", value=round(random()*90, 2)))
		# Climbing: grade normalized (0-10)
		db.add(Log(user_id=user.id, log_date=curr, domain="climbing", value=round(random()*10, 2)))
		# Coding: hours focused (0-8)
		db.add(Log(user_id=user.id, log_date=curr, domain="coding", value=round(random()*8, 2)))
		# Mood: 1-5
		db.add(Log(user_id=user.id, log_date=curr, domain="mood", value=round(1 + random()*4, 2)))
		# Sleep: hours (4-9)
		db.add(Log(user_id=user.id, log_date=curr, domain="sleep", value=round(4 + random()*5, 2)))
		# Journaling: note only
		note = f"Day {curr.isoformat()} reflections on training, coding, and mood."
		db.add(Log(user_id=user.id, log_date=curr, domain="journaling", value=None, note=note))
		curr += timedelta(days=1)
	db.commit()


def main():
	db: Session = SessionLocal()
	try:
		user = ensure_user(db, "demo@crosscoach.app", "Demo User")
		seed_logs(db, user)
		print("Seed complete for user:", user.id)
	finally:
		db.close()


if __name__ == "__main__":
	main() 