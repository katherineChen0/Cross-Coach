# Correlation Analysis Scripts

This directory contains scripts for analyzing correlations between user metrics and generating insights.

## Files

- `correlation_analysis.py` - Main correlation analysis script
- `test_correlation_analysis.py` - Test script with example usage
- `example_usage.py` - Comprehensive example showing different usage patterns
- `README.md` - This documentation file

## Overview

The correlation analysis system:

1. **Fetches all logs** for a specific user
2. **Groups by domain + metric** (e.g., "sleep_hours", "climbing_performance")
3. **Runs pairwise correlation tests** using Pearson correlation
4. **Selects top correlations** with p < 0.05 (top 3 positive, top 3 negative)
5. **Generates natural language insights** and stores them in the `CorrelationInsight` table

## Usage

### Command Line Usage

```bash
# Run analysis for a specific user
python correlation_analysis.py <user_id>

# Example
python correlation_analysis.py 123e4567-e89b-12d3-a456-426614174000
```

### Programmatic Usage

```python
from correlation_analysis import run_correlation_analysis
import uuid

# Run analysis for a user
user_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
results = run_correlation_analysis(user_id)

# Access results
print(f"Found {results['significant_correlations']} significant correlations")
for corr in results['positive_correlations']:
    print(f"Positive: {corr['insight']}")
```

### API Usage

The correlation analysis is also available via API endpoints:

```python
import requests

# Trigger analysis (requires authentication)
response = requests.post("http://localhost:8000/analyze-correlations", 
                        headers={"Authorization": "Bearer <token>"})
analysis_result = response.json()

# Get insights
response = requests.get("http://localhost:8000/insights",
                       headers={"Authorization": "Bearer <token>"})
insights = response.json()
```

### Testing

```bash
# Run the test script to see example correlations
python test_correlation_analysis.py

# Run the comprehensive example
python example_usage.py
```

## How It Works

### 1. Data Fetching
- Retrieves all `LogEntry` records for the specified user
- Converts to pandas DataFrame with columns: `date`, `domain`, `metric`, `value`

### 2. Data Grouping
- Creates unique identifiers for each domain-metric combination
- Pivots data so each metric becomes a column
- Handles multiple entries per day by averaging values

### 3. Correlation Analysis
- Performs pairwise Pearson correlation tests between all metrics
- Requires at least 3 data points for each correlation
- Calculates correlation coefficient and p-value for each pair

### 4. Insight Generation
- Filters for significant correlations (p < 0.05)
- Separates positive and negative correlations
- Generates natural language descriptions like:
  - "Higher sleep hours in sleep is associated with better performance in climbing (85.2% correlation)"
  - "Sleep hours and stress level show a strong negative correlation (67.8% inverse relationship)"

### 5. Database Storage
- Clears existing insights for the user
- Stores new insights in the `CorrelationInsight` table
- Each insight includes description and correlation score

## Example Insights

The system generates insights such as:

- **Positive correlations**: "Climbing performance improves by 30% when you sleep 7+ hours"
- **Negative correlations**: "Stress levels decrease by 25% with more exercise frequency"
- **Cross-domain insights**: "Higher sleep hours in sleep is associated with better mood in reflection"

## Requirements

- Python 3.8+
- pandas
- scipy
- SQLAlchemy
- PostgreSQL database with the Cross-Coach schema

## Database Schema

The script works with these tables:

- `users` - User information
- `log_entries` - User metric logs (date, domain, metric, value)
- `correlation_insights` - Generated insights (description, correlation_score)

## Error Handling

The script includes comprehensive error handling:

- Validates user ID format
- Checks for sufficient data (minimum 3 data points per correlation)
- Handles missing or invalid data gracefully
- Provides detailed error messages

## Performance Considerations

- Uses database indexes for efficient log retrieval
- Processes correlations in memory for speed
- Limits to top 3 positive/negative correlations to manage output size
- Clears old insights before creating new ones to prevent accumulation 