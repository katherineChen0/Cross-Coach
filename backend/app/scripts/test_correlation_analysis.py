#!/usr/bin/env python3
"""
Test script for correlation analysis functionality.

This script demonstrates how to use the correlation analysis module
and provides example usage patterns.
"""

import sys
import os
import uuid
from datetime import date, timedelta

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import User, LogEntry, CorrelationInsight, DomainEnum
from correlation_analysis import run_correlation_analysis


def create_test_data(db, user_id):
    """
    Create sample test data for correlation analysis.
    
    This creates realistic log entries that should show some correlations:
    - Sleep hours vs climbing performance (positive correlation)
    - Sleep hours vs stress level (negative correlation)
    - Exercise frequency vs mood (positive correlation)
    """
    
    # Create a test user if it doesn't exist
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            name="Test User",
            email="test@example.com",
            password_hash="dummy_hash"
        )
        db.add(user)
        db.commit()
    
    # Clear existing log entries for this user
    db.query(LogEntry).filter(LogEntry.user_id == user_id).delete()
    
    # Generate 30 days of test data
    base_date = date.today() - timedelta(days=30)
    log_entries = []
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        
        # Sleep data (6-9 hours, with some variation)
        sleep_hours = 7.5 + (i % 7 - 3) * 0.5  # Varies around 7.5 hours
        
        # Climbing performance (correlated with sleep)
        climbing_performance = 6.0 + sleep_hours * 0.3 + (i % 5 - 2) * 0.5
        
        # Stress level (inversely correlated with sleep)
        stress_level = 10.0 - sleep_hours * 0.8 + (i % 3 - 1) * 0.5
        
        # Exercise frequency (independent)
        exercise_frequency = 3 + (i % 4 - 1)
        
        # Mood (correlated with exercise)
        mood = 7.0 + exercise_frequency * 0.5 + (i % 6 - 2) * 0.3
        
        # Create log entries
        entries = [
            LogEntry(
                user_id=user_id,
                date=current_date,
                domain=DomainEnum.sleep,
                metric="hours",
                value=sleep_hours
            ),
            LogEntry(
                user_id=user_id,
                date=current_date,
                domain=DomainEnum.climbing,
                metric="performance",
                value=climbing_performance
            ),
            LogEntry(
                user_id=user_id,
                date=current_date,
                domain=DomainEnum.reflection,
                metric="stress_level",
                value=stress_level
            ),
            LogEntry(
                user_id=user_id,
                date=current_date,
                domain=DomainEnum.fitness,
                metric="exercise_frequency",
                value=exercise_frequency
            ),
            LogEntry(
                user_id=user_id,
                date=current_date,
                domain=DomainEnum.reflection,
                metric="mood",
                value=mood
            )
        ]
        
        log_entries.extend(entries)
    
    db.add_all(log_entries)
    db.commit()
    
    print(f"Created {len(log_entries)} test log entries for user {user_id}")


def display_insights(db, user_id):
    """Display the generated insights from the database."""
    insights = db.query(CorrelationInsight).filter(
        CorrelationInsight.user_id == user_id
    ).order_by(CorrelationInsight.correlation_score.desc()).all()
    
    print("\n=== STORED INSIGHTS ===")
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight.description}")
        print(f"   Correlation Score: {insight.correlation_score:.3f}")
        print(f"   Created: {insight.created_at}")
        print()


def main():
    """Main test function."""
    # Use a fixed test user ID
    test_user_id = uuid.uuid4()
    
    print("=== CORRELATION ANALYSIS TEST ===")
    print(f"Test User ID: {test_user_id}")
    
    db = SessionLocal()
    
    try:
        # Create test data
        print("\n1. Creating test data...")
        create_test_data(db, test_user_id)
        
        # Run correlation analysis
        print("\n2. Running correlation analysis...")
        results = run_correlation_analysis(test_user_id)
        
        # Display results
        print("\n3. Analysis Results:")
        print(f"   Total logs: {results['total_logs']}")
        print(f"   Total metrics: {results['total_metrics']}")
        print(f"   Significant correlations: {results['significant_correlations']}")
        
        # Display insights from database
        print("\n4. Displaying stored insights...")
        display_insights(db, test_user_id)
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main() 