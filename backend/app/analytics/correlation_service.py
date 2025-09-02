import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from ..models import LogEntry, CorrelationInsight, User
from ..db import get_db
import logging

logger = logging.getLogger(__name__)

class CorrelationService:
    """Service for computing correlations between user metrics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_data_as_dataframe(self, user_id: str, days_back: int = 90) -> pd.DataFrame:
        """Get user log entries as a pandas DataFrame for analysis."""
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        
        # Get all log entries for the user within the time period
        stmt = select(LogEntry).where(
            LogEntry.user_id == user_id,
            LogEntry.date >= cutoff_date
        ).order_by(LogEntry.date)
        
        entries = self.db.execute(stmt).scalars().all()
        
        if not entries:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for entry in entries:
            data.append({
                'date': entry.date,
                'domain': entry.domain.value,
                'metric': entry.metric,
                'value': entry.value,
                'notes': entry.notes
            })
        
        df = pd.DataFrame(data)
        return df
    
    def compute_correlations(self, user_id: str) -> List[Dict]:
        """Compute correlations between different metrics for a user."""
        df = self.get_user_data_as_dataframe(user_id)
        
        if df.empty:
            logger.info(f"No data found for user {user_id}")
            return []
        
        # Pivot data to get metrics as columns
        # Group by date and domain-metric combination
        df['metric_key'] = df['domain'] + '_' + df['metric']
        
        # Create pivot table with date as index and metric_key as columns
        pivot_df = df.pivot_table(
            index='date',
            columns='metric_key',
            values='value',
            aggfunc='mean'  # Average multiple entries per day
        ).fillna(method='ffill').fillna(0)  # Forward fill and fill remaining NaN with 0
        
        if pivot_df.shape[1] < 2:
            logger.info(f"Not enough different metrics for user {user_id} to compute correlations")
            return []
        
        correlations = []
        
        # Compute correlations between all pairs of metrics
        for i, col1 in enumerate(pivot_df.columns):
            for col2 in pivot_df.columns[i+1:]:
                try:
                    # Remove rows where either column has NaN values
                    clean_data = pivot_df[[col1, col2]].dropna()
                    
                    if len(clean_data) < 5:  # Need at least 5 data points
                        continue
                    
                    # Compute Pearson correlation
                    corr_coef, p_value = pearsonr(clean_data[col1], clean_data[col2])
                    
                    # Only include significant correlations (p < 0.05) and moderate strength (|r| > 0.3)
                    if p_value < 0.05 and abs(corr_coef) > 0.3:
                        correlation_info = {
                            'metric1': col1,
                            'metric2': col2,
                            'correlation_coefficient': corr_coef,
                            'p_value': p_value,
                            'data_points': len(clean_data),
                            'description': self._generate_correlation_description(col1, col2, corr_coef)
                        }
                        correlations.append(correlation_info)
                        
                except Exception as e:
                    logger.warning(f"Error computing correlation between {col1} and {col2}: {e}")
                    continue
        
        return correlations
    
    def _generate_correlation_description(self, metric1: str, metric2: str, corr_coef: float) -> str:
        """Generate a human-readable description of the correlation."""
        strength = "strong" if abs(corr_coef) > 0.7 else "moderate" if abs(corr_coef) > 0.5 else "weak"
        direction = "positive" if corr_coef > 0 else "negative"
        
        # Clean up metric names for display
        m1_clean = metric1.replace('_', ' ').title()
        m2_clean = metric2.replace('_', ' ').title()
        
        return f"{strength.title()} {direction} correlation ({corr_coef:.2f}) between {m1_clean} and {m2_clean}"
    
    def save_correlation_insights(self, user_id: str, correlations: List[Dict]) -> None:
        """Save correlation insights to the database."""
        # Clear existing insights for this user
        self.db.query(CorrelationInsight).filter(CorrelationInsight.user_id == user_id).delete()
        
        # Save new insights
        for corr in correlations:
            insight = CorrelationInsight(
                user_id=user_id,
                description=corr['description'],
                correlation_score=corr['correlation_coefficient']
            )
            self.db.add(insight)
        
        self.db.commit()
        logger.info(f"Saved {len(correlations)} correlation insights for user {user_id}")
    
    def run_weekly_analysis(self) -> None:
        """Run weekly correlation analysis for all users."""
        logger.info("Starting weekly correlation analysis")
        
        # Get all users
        users = self.db.query(User).all()
        
        for user in users:
            try:
                logger.info(f"Computing correlations for user {user.id}")
                correlations = self.compute_correlations(str(user.id))
                self.save_correlation_insights(str(user.id), correlations)
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {e}")
                continue
        
        logger.info("Weekly correlation analysis completed")


def run_weekly_correlation_analysis():
    """Function to be called by the background task scheduler."""
    from ..db import SessionLocal
    
    db = SessionLocal()
    try:
        service = CorrelationService(db)
        service.run_weekly_analysis()
    finally:
        db.close() 