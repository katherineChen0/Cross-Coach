#!/usr/bin/env python3
"""
Example usage of correlation analysis functionality.

This script demonstrates how to:
1. Create test data for a user
2. Run correlation analysis
3. Retrieve insights via API
4. Use the analysis programmatically
"""

import sys
import os
import uuid
import requests
import json
from datetime import date, timedelta

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import User, LogEntry, CorrelationInsight, DomainEnum
from correlation_analysis import run_correlation_analysis


def create_sample_user_data():
    """Create a sample user with realistic log data."""
    db = SessionLocal()
    
    try:
        # Create a test user
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            name="Sample User",
            email="sample@example.com",
            password_hash="dummy_hash"
        )
        db.add(user)
        db.commit()
        
        # Generate 60 days of realistic data
        base_date = date.today() - timedelta(days=60)
        log_entries = []
        
        for i in range(60):
            current_date = base_date + timedelta(days=i)
            
            # Sleep pattern (varies by day of week)
            day_of_week = current_date.weekday()
            if day_of_week < 5:  # Weekdays
                sleep_hours = 7.0 + (i % 3 - 1) * 0.5
            else:  # Weekends
                sleep_hours = 8.5 + (i % 4 - 2) * 0.5
            
            # Climbing performance (correlated with sleep and day of week)
            climbing_performance = 6.5 + sleep_hours * 0.2 + (day_of_week < 5) * 0.5 + (i % 7 - 3) * 0.3
            
            # Stress level (inversely correlated with sleep, higher on weekdays)
            stress_level = 8.0 - sleep_hours * 0.4 + (day_of_week < 5) * 1.0 + (i % 5 - 2) * 0.4
            
            # Exercise frequency (more on weekdays, varies)
            exercise_frequency = 4 + (day_of_week < 5) * 1 + (i % 6 - 2)
            
            # Mood (correlated with exercise and sleep, better on weekends)
            mood = 6.5 + exercise_frequency * 0.3 + sleep_hours * 0.2 + (day_of_week >= 5) * 0.5 + (i % 8 - 4) * 0.2
            
            # Learning hours (more on weekdays)
            learning_hours = 2.0 + (day_of_week < 5) * 1.5 + (i % 4 - 1) * 0.5
            
            # Create log entries
            entries = [
                LogEntry(user_id=user_id, date=current_date, domain=DomainEnum.sleep, metric="hours", value=sleep_hours),
                LogEntry(user_id=user_id, date=current_date, domain=DomainEnum.climbing, metric="performance", value=climbing_performance),
                LogEntry(user_id=user_id, date=current_date, domain=DomainEnum.reflection, metric="stress_level", value=stress_level),
                LogEntry(user_id=user_id, date=current_date, domain=DomainEnum.fitness, metric="exercise_frequency", value=exercise_frequency),
                LogEntry(user_id=user_id, date=current_date, domain=DomainEnum.reflection, metric="mood", value=mood),
                LogEntry(user_id=user_id, date=current_date, domain=DomainEnum.learning, metric="hours", value=learning_hours),
            ]
            
            log_entries.extend(entries)
        
        db.add_all(log_entries)
        db.commit()
        
        print(f"Created user {user_id} with {len(log_entries)} log entries")
        return user_id
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def example_programmatic_usage(user_id):
    """Example of using correlation analysis programmatically."""
    print("\n=== PROGRAMMATIC USAGE EXAMPLE ===")
    
    try:
        # Run correlation analysis
        results = run_correlation_analysis(user_id)
        
        print(f"Analysis completed for user {user_id}")
        print(f"Total logs analyzed: {results['total_logs']}")
        print(f"Metrics found: {results['total_metrics']}")
        print(f"Significant correlations: {results['significant_correlations']}")
        
        # Display top positive correlations
        print("\nTop Positive Correlations:")
        for i, corr in enumerate(results['positive_correlations'][:3], 1):
            print(f"{i}. {corr['insight']}")
            print(f"   Correlation: {corr['correlation']:.3f}, p-value: {corr['p_value']:.4f}")
        
        # Display top negative correlations
        print("\nTop Negative Correlations:")
        for i, corr in enumerate(results['negative_correlations'][:3], 1):
            print(f"{i}. {corr['insight']}")
            print(f"   Correlation: {corr['correlation']:.3f}, p-value: {corr['p_value']:.4f}")
        
        return results
        
    except Exception as e:
        print(f"Error in programmatic analysis: {e}")
        return None


def example_api_usage(base_url="http://localhost:8000"):
    """Example of using correlation analysis via API."""
    print("\n=== API USAGE EXAMPLE ===")
    
    # Note: This would require authentication in a real scenario
    # For demonstration, we'll show the API structure
    
    print("API Endpoints available:")
    print(f"POST {base_url}/analyze-correlations")
    print("  - Triggers correlation analysis for authenticated user")
    print("  - Returns analysis summary")
    
    print(f"GET {base_url}/insights")
    print("  - Retrieves stored correlation insights")
    print("  - Returns list of insights with descriptions")
    
    print("\nExample API response structure:")
    example_response = {
        "message": "Correlation analysis completed successfully",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "total_logs": 360,
        "total_metrics": 6,
        "significant_correlations": 8,
        "insights_generated": 6
    }
    print(json.dumps(example_response, indent=2))


def display_insights_from_db(user_id):
    """Display insights stored in the database."""
    print("\n=== INSIGHTS FROM DATABASE ===")
    
    db = SessionLocal()
    try:
        insights = db.query(CorrelationInsight).filter(
            CorrelationInsight.user_id == user_id
        ).order_by(CorrelationInsight.correlation_score.desc()).all()
        
        if not insights:
            print("No insights found in database.")
            return
        
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight.description}")
            print(f"   Correlation Score: {insight.correlation_score:.3f}")
            print(f"   Created: {insight.created_at}")
            print()
            
    except Exception as e:
        print(f"Error retrieving insights: {e}")
    finally:
        db.close()


def main():
    """Main example function."""
    print("=== CORRELATION ANALYSIS EXAMPLE ===")
    
    try:
        # Create sample data
        print("1. Creating sample user data...")
        user_id = create_sample_user_data()
        
        # Run programmatic analysis
        print("2. Running programmatic analysis...")
        results = example_programmatic_usage(user_id)
        
        # Display insights from database
        print("3. Displaying insights from database...")
        display_insights_from_db(user_id)
        
        # Show API usage example
        print("4. API usage example...")
        example_api_usage()
        
        print("\n=== EXAMPLE COMPLETED ===")
        print("The correlation analysis system successfully:")
        print("- Created realistic test data")
        print("- Performed correlation analysis")
        print("- Generated natural language insights")
        print("- Stored insights in the database")
        
    except Exception as e:
        print(f"Error in example: {e}")


if __name__ == "__main__":
    main() 