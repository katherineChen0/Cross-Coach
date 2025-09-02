#!/usr/bin/env python3
"""
Test script for the AI functions: summarize_journal and generate_ai_coach_insights
"""

import os
import sys
from datetime import date
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services import summarize_journal, generate_ai_coach_insights
from app.models import LogEntry, CorrelationInsight, DomainEnum
from app.core.config import settings

def test_summarize_journal():
    """Test the journal summarization function."""
    print("Testing journal summarization...")
    
    # Sample journal text
    journal_text = """
    Today was quite challenging. I had a difficult conversation with my manager about project deadlines, 
    and I'm feeling overwhelmed with the workload. However, I did manage to go for a 30-minute walk 
    during lunch which helped clear my mind. I also spent some time reading a book before bed, 
    which was relaxing. I'm trying to focus on the positive aspects of the day and practice gratitude.
    """
    
    try:
        summary = summarize_journal(journal_text)
        print(f"Original text: {journal_text.strip()}")
        print(f"Summary: {summary}")
        print("✓ Journal summarization test completed\n")
    except Exception as e:
        print(f"✗ Journal summarization test failed: {e}\n")

def test_ai_coach_insights():
    """Test the AI coach insights function."""
    print("Testing AI coach insights...")
    
    # Sample log entries
    sample_logs = [
        LogEntry(
            id="1",
            user_id="test-user",
            date=date(2024, 1, 15),
            domain=DomainEnum.fitness,
            metric="workout_duration",
            value=45.0,
            notes="Morning run, felt energized"
        ),
        LogEntry(
            id="2", 
            user_id="test-user",
            date=date(2024, 1, 15),
            domain=DomainEnum.sleep,
            metric="sleep_hours",
            value=7.5,
            notes="Good quality sleep"
        ),
        LogEntry(
            id="3",
            user_id="test-user", 
            date=date(2024, 1, 14),
            domain=DomainEnum.fitness,
            metric="workout_duration",
            value=30.0,
            notes="Quick workout, busy day"
        ),
        LogEntry(
            id="4",
            user_id="test-user",
            date=date(2024, 1, 14),
            domain=DomainEnum.sleep,
            metric="sleep_hours", 
            value=6.0,
            notes="Woke up early for meeting"
        )
    ]
    
    # Sample correlation insights
    sample_correlations = [
        CorrelationInsight(
            id="1",
            user_id="test-user",
            description="Higher sleep hours correlate with longer workout duration",
            correlation_score=0.75
        ),
        CorrelationInsight(
            id="2", 
            user_id="test-user",
            description="Morning workouts tend to be more consistent",
            correlation_score=0.82
        )
    ]
    
    try:
        insights = generate_ai_coach_insights(sample_logs, sample_correlations)
        print(f"Generated insights: {insights}")
        print("✓ AI coach insights test completed\n")
    except Exception as e:
        print(f"✗ AI coach insights test failed: {e}\n")

def main():
    """Run all tests."""
    print("AI Functions Test Suite")
    print("=" * 50)
    
    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        print("⚠️  OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
        print("Tests will fail but you can see the function structure.\n")
    
    test_summarize_journal()
    test_ai_coach_insights()
    
    print("Test suite completed!")

if __name__ == "__main__":
    main() 