#!/usr/bin/env python3
"""
Correlation Analysis Script

This script fetches all logs for a user, groups them by domain + metric,
runs pairwise correlation tests between metrics, and generates insights
about significant correlations.
"""

import sys
import os
import uuid
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from scipy import stats
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.db import SessionLocal
from app.models import User, LogEntry, CorrelationInsight, DomainEnum


def fetch_user_logs(db: Session, user_id: uuid.UUID) -> pd.DataFrame:
    """
    Fetch all logs for a specific user and return as a pandas DataFrame.
    
    Args:
        db: Database session
        user_id: UUID of the user
        
    Returns:
        DataFrame with columns: date, domain, metric, value
    """
    logs = db.query(LogEntry).filter(LogEntry.user_id == user_id).all()
    
    if not logs:
        raise ValueError(f"No logs found for user {user_id}")
    
    data = []
    for log in logs:
        data.append({
            'date': log.date,
            'domain': log.domain.value,
            'metric': log.metric,
            'value': log.value
        })
    
    return pd.DataFrame(data)


def group_logs_by_domain_metric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group logs by domain + metric and pivot to create a wide format
    where each metric becomes a column.
    
    Args:
        df: DataFrame with log entries
        
    Returns:
        Pivoted DataFrame with dates as index and metrics as columns
    """
    # Create a unique identifier for each domain-metric combination
    df['domain_metric'] = df['domain'] + '_' + df['metric']
    
    # Pivot the data to get metrics as columns
    pivoted = df.pivot_table(
        index='date',
        columns='domain_metric',
        values='value',
        aggfunc='mean'  # In case of multiple entries per day
    )
    
    return pivoted


def calculate_correlations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate pairwise correlations between all metrics.
    
    Args:
        df: Pivoted DataFrame with metrics as columns
        
    Returns:
        List of correlation results with p-values
    """
    correlations = []
    metrics = df.columns.tolist()
    
    for i, metric1 in enumerate(metrics):
        for j, metric2 in enumerate(metrics):
            if i >= j:  # Skip duplicate pairs and self-correlations
                continue
                
            # Get the two series, removing NaN values
            series1 = df[metric1].dropna()
            series2 = df[metric2].dropna()
            
            # Find common dates
            common_dates = series1.index.intersection(series2.index)
            
            if len(common_dates) < 3:  # Need at least 3 data points
                continue
                
            # Get values for common dates
            values1 = series1.loc[common_dates]
            values2 = series2.loc[common_dates]
            
            # Calculate correlation
            correlation, p_value = stats.pearsonr(values1, values2)
            
            # Skip if correlation is NaN
            if np.isnan(correlation):
                continue
                
            correlations.append({
                'metric1': metric1,
                'metric2': metric2,
                'correlation': correlation,
                'p_value': p_value,
                'n_samples': len(common_dates)
            })
    
    return correlations


def select_top_correlations(correlations: List[Dict[str, Any]], 
                          top_n: int = 3) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Select top positive and negative correlations with p < 0.05.
    
    Args:
        correlations: List of correlation results
        top_n: Number of top correlations to select
        
    Returns:
        Tuple of (positive_correlations, negative_correlations)
    """
    # Filter for significant correlations (p < 0.05)
    significant = [c for c in correlations if c['p_value'] < 0.05]
    
    # Separate positive and negative correlations
    positive = [c for c in significant if c['correlation'] > 0]
    negative = [c for c in significant if c['correlation'] < 0]
    
    # Sort by absolute correlation value and take top N
    positive.sort(key=lambda x: abs(x['correlation']), reverse=True)
    negative.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return positive[:top_n], negative[:top_n]


def generate_insight_text(correlation: Dict[str, Any]) -> str:
    """
    Generate natural language insight from correlation data.
    
    Args:
        correlation: Correlation result dictionary
        
    Returns:
        Natural language insight string
    """
    metric1 = correlation['metric1']
    metric2 = correlation['metric2']
    corr_value = correlation['correlation']
    p_value = correlation['p_value']
    
    # Parse domain and metric names
    domain1, metric_name1 = metric1.split('_', 1)
    domain2, metric_name2 = metric2.split('_', 1)
    
    # Format correlation as percentage
    corr_percent = abs(corr_value) * 100
    
    if corr_value > 0:
        if domain1 == domain2:
            insight = f"{metric_name1.title()} and {metric_name2} show a strong positive correlation ({corr_percent:.1f}% relationship)"
        else:
            insight = f"Higher {metric_name1} in {domain1} is associated with better {metric_name2} in {domain2} ({corr_percent:.1f}% correlation)"
    else:
        if domain1 == domain2:
            insight = f"{metric_name1.title()} and {metric_name2} show a strong negative correlation ({corr_percent:.1f}% inverse relationship)"
        else:
            insight = f"Higher {metric_name1} in {domain1} is associated with lower {metric_name2} in {domain2} ({corr_percent:.1f}% inverse correlation)"
    
    # Add significance note
    if p_value < 0.01:
        insight += " (highly significant)"
    elif p_value < 0.05:
        insight += " (significant)"
    
    return insight


def save_insights_to_db(db: Session, user_id: uuid.UUID, 
                       positive_correlations: List[Dict[str, Any]],
                       negative_correlations: List[Dict[str, Any]]) -> None:
    """
    Save correlation insights to the database.
    
    Args:
        db: Database session
        user_id: UUID of the user
        positive_correlations: List of positive correlation results
        negative_correlations: List of negative correlation results
    """
    # Clear existing insights for this user
    db.query(CorrelationInsight).filter(CorrelationInsight.user_id == user_id).delete()
    
    # Create insights for positive correlations
    for corr in positive_correlations:
        insight = CorrelationInsight(
            user_id=user_id,
            description=generate_insight_text(corr),
            correlation_score=corr['correlation']
        )
        db.add(insight)
    
    # Create insights for negative correlations
    for corr in negative_correlations:
        insight = CorrelationInsight(
            user_id=user_id,
            description=generate_insight_text(corr),
            correlation_score=corr['correlation']
        )
        db.add(insight)
    
    db.commit()


def run_correlation_analysis(user_id: uuid.UUID) -> Dict[str, Any]:
    """
    Main function to run the complete correlation analysis.
    
    Args:
        user_id: UUID of the user to analyze
        
    Returns:
        Dictionary with analysis results
    """
    db = SessionLocal()
    
    try:
        # Fetch user logs
        print(f"Fetching logs for user {user_id}...")
        logs_df = fetch_user_logs(db, user_id)
        print(f"Found {len(logs_df)} log entries")
        
        # Group by domain + metric
        print("Grouping logs by domain and metric...")
        pivoted_df = group_logs_by_domain_metric(logs_df)
        print(f"Created {len(pivoted_df.columns)} metric columns")
        
        # Calculate correlations
        print("Calculating pairwise correlations...")
        correlations = calculate_correlations(pivoted_df)
        print(f"Found {len(correlations)} correlation pairs")
        
        # Select top correlations
        print("Selecting top correlations...")
        positive_corr, negative_corr = select_top_correlations(correlations)
        
        # Save insights to database
        print("Saving insights to database...")
        save_insights_to_db(db, user_id, positive_corr, negative_corr)
        
        # Prepare results
        results = {
            'user_id': str(user_id),
            'total_logs': len(logs_df),
            'total_metrics': len(pivoted_df.columns),
            'total_correlations': len(correlations),
            'significant_correlations': len(positive_corr) + len(negative_corr),
            'positive_correlations': [
                {
                    'metrics': f"{c['metric1']} vs {c['metric2']}",
                    'correlation': c['correlation'],
                    'p_value': c['p_value'],
                    'insight': generate_insight_text(c)
                }
                for c in positive_corr
            ],
            'negative_correlations': [
                {
                    'metrics': f"{c['metric1']} vs {c['metric2']}",
                    'correlation': c['correlation'],
                    'p_value': c['p_value'],
                    'insight': generate_insight_text(c)
                }
                for c in negative_corr
            ]
        }
        
        print("Analysis complete!")
        return results
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to run the script from command line."""
    if len(sys.argv) != 2:
        print("Usage: python correlation_analysis.py <user_id>")
        sys.exit(1)
    
    try:
        user_id = uuid.UUID(sys.argv[1])
    except ValueError:
        print("Invalid user ID format. Please provide a valid UUID.")
        sys.exit(1)
    
    try:
        results = run_correlation_analysis(user_id)
        
        print("\n=== CORRELATION ANALYSIS RESULTS ===")
        print(f"User ID: {results['user_id']}")
        print(f"Total logs analyzed: {results['total_logs']}")
        print(f"Total metrics: {results['total_metrics']}")
        print(f"Total correlations tested: {results['total_correlations']}")
        print(f"Significant correlations found: {results['significant_correlations']}")
        
        print("\n=== TOP POSITIVE CORRELATIONS ===")
        for i, corr in enumerate(results['positive_correlations'], 1):
            print(f"{i}. {corr['insight']}")
            print(f"   Correlation: {corr['correlation']:.3f}, p-value: {corr['p_value']:.4f}")
        
        print("\n=== TOP NEGATIVE CORRELATIONS ===")
        for i, corr in enumerate(results['negative_correlations'], 1):
            print(f"{i}. {corr['insight']}")
            print(f"   Correlation: {corr['correlation']:.3f}, p-value: {corr['p_value']:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 