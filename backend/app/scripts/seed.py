from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from ..db import SessionLocal
import hashlib
import random
import json


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def ensure_user(db: Session, email: str, name: str, password: str):
    """Ensure user exists, create if not"""
    # Check if user exists
    result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
    user = result.fetchone()
    
    if user:
        print(f"User {email} already exists")
        return user[0]
    
    # Create user with hashed password
    # First, add password_hash column if it doesn't exist
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN password_hash TEXT"))
        db.commit()
    except Exception:
        # Column already exists
        pass
    
    result = db.execute(
        text("INSERT INTO users (email, name, password_hash) VALUES (:email, :name, :password_hash) RETURNING id"),
        {
            "email": email,
            "name": name,
            "password_hash": hash_password(password)
        }
    )
    user_id = result.fetchone()[0]
    db.commit()
    print(f"Created user {email} with ID: {user_id}")
    return user_id


def seed_logs(db: Session, user_id):
    """Seed 2 weeks of realistic data with correlations"""
    end = date.today()
    start = end - timedelta(days=13)  # 2 weeks
    curr = start
    
    # Track sleep hours to create correlations
    sleep_data = {}
    
    while curr <= end:
        # Sleep: hours (4-9) - create some days with 7+ hours
        sleep_hours = random.uniform(4, 9)
        if random.random() < 0.4:  # 40% chance of 7+ hours
            sleep_hours = random.uniform(7, 9)
        sleep_data[curr] = sleep_hours
        db.execute(
            text("INSERT INTO logs (user_id, log_date, domain, value) VALUES (:user_id, :log_date, 'sleep', :value)"),
            {
                "user_id": user_id,
                "log_date": curr,
                "value": round(sleep_hours, 1)
            }
        )
        
        # Climbing: grade normalized (0-10) - better after good sleep
        base_climbing = random.uniform(3, 8)
        if sleep_data[curr] >= 7:
            base_climbing += random.uniform(1, 2)  # 25% better after 7+ hours sleep
        climbing_grade = min(10, round(base_climbing, 1))
        db.execute(
            text("INSERT INTO logs (user_id, log_date, domain, value) VALUES (:user_id, :log_date, 'climbing', :value)"),
            {
                "user_id": user_id,
                "log_date": curr,
                "value": climbing_grade
            }
        )
        
        # Fitness: minutes trained (0-90)
        fitness_minutes = random.uniform(0, 90)
        db.execute(
            text("INSERT INTO logs (user_id, log_date, domain, value) VALUES (:user_id, :log_date, 'fitness', :value)"),
            {
                "user_id": user_id,
                "log_date": curr,
                "value": round(fitness_minutes, 1)
            }
        )
        
        # Coding: hours focused (0-8) - some days with >3h
        coding_hours = random.uniform(0, 8)
        if random.random() < 0.3:  # 30% chance of >3h coding
            coding_hours = random.uniform(3, 8)
        db.execute(
            text("INSERT INTO logs (user_id, log_date, domain, value) VALUES (:user_id, :log_date, 'coding', :value)"),
            {
                "user_id": user_id,
                "log_date": curr,
                "value": round(coding_hours, 1)
            }
        )
        
        # Mood: 1-5 - dips on days with >3h coding but no exercise
        base_mood = random.uniform(3, 5)
        if coding_hours > 3 and fitness_minutes < 30:
            base_mood -= random.uniform(1, 2)  # Mood dip
        mood_rating = max(1, min(5, round(base_mood, 1)))
        db.execute(
            text("INSERT INTO logs (user_id, log_date, domain, value) VALUES (:user_id, :log_date, 'mood', :value)"),
            {
                "user_id": user_id,
                "log_date": curr,
                "value": mood_rating
            }
        )
        
        # Journaling: note only
        note = f"Day {curr.isoformat()}: Sleep {sleep_data[curr]:.1f}h, Climbing {climbing_grade}, Coding {coding_hours:.1f}h, Mood {mood_rating:.1f}. "
        if sleep_data[curr] >= 7:
            note += "Feeling well-rested today. "
        if coding_hours > 3 and fitness_minutes < 30:
            note += "Long coding session without exercise - feeling a bit drained. "
        if fitness_minutes > 60:
            note += "Great workout session! "
        
        db.execute(
            text("INSERT INTO logs (user_id, log_date, domain, note) VALUES (:user_id, :log_date, 'journaling', :note)"),
            {
                "user_id": user_id,
                "log_date": curr,
                "note": note
            }
        )
        
        curr += timedelta(days=1)
    
    db.commit()


def generate_example_insights(db: Session, user_id):
    """Generate example insights from seed data"""
    # Clear existing insights
    db.execute(text("DELETE FROM insights WHERE user_id = :user_id"), {"user_id": user_id})
    
    # Generate example insights
    insights = [
        {
            "week_start": (date.today() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "summary": "This week showed strong correlations between sleep quality and climbing performance. Days with 7+ hours of sleep resulted in 25% better climbing grades. Additionally, mood was significantly lower on days with extended coding sessions (>3 hours) without accompanying exercise.",
            "correlations": {
                "sleep_climbing": {
                    "description": "Climbing sessions are 25% better after 7+ hours of sleep",
                    "correlation_score": 0.78,
                    "data_points": 7
                },
                "coding_mood": {
                    "description": "Mood dips on days with >3h coding but no exercise",
                    "correlation_score": -0.65,
                    "data_points": 3
                },
                "sleep_overall": {
                    "description": "Sleep quality significantly impacts overall performance",
                    "correlation_score": 0.82,
                    "data_points": 7
                }
            }
        },
        {
            "week_start": (date.today() - timedelta(days=14)).strftime("%Y-%m-%d"),
            "summary": "Previous week analysis revealed that regular exercise helps maintain mood during intensive coding periods. The data shows that combining physical activity with mental work leads to better overall well-being and performance.",
            "correlations": {
                "exercise_mood": {
                    "description": "Regular exercise helps maintain mood during intensive coding periods",
                    "correlation_score": 0.71,
                    "data_points": 7
                },
                "sleep_consistency": {
                    "description": "Consistent sleep schedule improves daily performance",
                    "correlation_score": 0.68,
                    "data_points": 7
                }
            }
        }
    ]
    
    # Insert insights
    for insight in insights:
        db.execute(
            text("""
                INSERT INTO insights (user_id, week_start, summary, correlations)
                VALUES (:user_id, :week_start, :summary, :correlations)
            """),
            {
                "user_id": user_id,
                "week_start": insight["week_start"],
                "summary": insight["summary"],
                "correlations": json.dumps(insight["correlations"])
            }
        )
    
    db.commit()


def main():
    db: Session = SessionLocal()
    try:
        # Create the specific user as requested
        user_id = ensure_user(db, "kath@example.com", "Kath", "password123")
        
        # Clear existing logs for this user
        db.execute(text("DELETE FROM logs WHERE user_id = :user_id"), {"user_id": user_id})
        db.commit()
        print("Cleared existing logs for user")
        
        # Seed new logs
        seed_logs(db, user_id)
        print("Seeded 2 weeks of sample data with correlations")
        
        # Generate example insights
        generate_example_insights(db, user_id)
        print("Generated example insights")
        
        # Print summary
        result = db.execute(text("SELECT COUNT(*) FROM logs WHERE user_id = :user_id"), {"user_id": user_id})
        log_count = result.fetchone()[0]
        print(f"Total logs created: {log_count}")
        
        # Show some example correlations
        print("\nExample correlations in the data:")
        print("- Climbing sessions are 25% better after 7+ hours of sleep")
        print("- Mood dips on days with >3h coding but no exercise")
        print("- Sleep quality affects overall performance")
        print("- Regular exercise helps maintain mood during intensive coding periods")
        
    finally:
        db.close()


if __name__ == "__main__":
    main() 