from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import SessionLocal
import json
from datetime import date, timedelta


def generate_example_insights():
    """Generate example insights from seed data"""
    db: Session = SessionLocal()
    try:
        # Get user
        result = db.execute(text("SELECT id FROM users WHERE email = 'kath@example.com'"))
        user = result.fetchone()
        if not user:
            print("User not found. Run seed script first.")
            return
        
        user_id = user[0]
        
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
        print("Generated example insights:")
        print("- Climbing sessions are 25% better after 7+ hours of sleep")
        print("- Mood dips on days with >3h coding but no exercise")
        print("- Sleep quality significantly impacts overall performance")
        print("- Regular exercise helps maintain mood during intensive coding periods")
        
    finally:
        db.close()


if __name__ == "__main__":
    generate_example_insights() 