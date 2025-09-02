# AI Functions Documentation

This document describes the AI-powered functions added to the Cross-Coach backend for journal summarization and AI coach insights.

## Overview

Two main AI functions have been implemented:

1. **`summarize_journal(text: str) -> str`** - Summarizes journal entries using OpenAI GPT
2. **`generate_ai_coach_insights(logs, correlations) -> str`** - Generates personalized coaching recommendations

## Setup

### 1. Environment Configuration

Add your OpenAI API key to your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1  # Default OpenAI endpoint
OPENAI_MODEL=gpt-4o-mini  # Default model
```

### 2. Install Dependencies

The OpenAI package has been added to `requirements.txt`. Install it with:

```bash
pip install -r requirements.txt
```

## Function Details

### `summarize_journal(text: str) -> str`

**Purpose**: Summarizes journal text into 2-3 sentences using AI.

**Parameters**:
- `text` (str): The journal text to summarize

**Returns**:
- `str`: A 2-3 sentence summary

**Features**:
- Uses OpenAI GPT API for intelligent summarization
- Fallback to simple text truncation if API fails
- Configurable model and parameters
- Error handling for API failures

**Example Usage**:
```python
from app.services import summarize_journal

journal_text = "Today was challenging but I managed to..."
summary = summarize_journal(journal_text)
print(summary)
# Output: "The day presented challenges but the user showed resilience..."
```

### `generate_ai_coach_insights(logs, correlations) -> str`

**Purpose**: Generates personalized coaching recommendations based on user data.

**Parameters**:
- `logs` (list[LogEntry]): User's log entries
- `correlations` (list[CorrelationInsight]): Correlation insights

**Returns**:
- `str`: 1-2 weekly recommendations in natural language

**Features**:
- Analyzes recent user activity (last 50 entries)
- Incorporates correlation insights
- Provides specific, actionable advice
- Supportive and encouraging tone
- Configurable analysis depth

**Example Usage**:
```python
from app.services import generate_ai_coach_insights

logs = get_user_logs(db, user_id)
correlations = get_user_correlations(db, user_id)
insights = generate_ai_coach_insights(logs, correlations)
print(insights)
# Output: "Based on your recent patterns, I recommend..."
```

## Database Integration

### JournalSummary Model

The `JournalSummary` model stores AI-generated summaries:

```python
class JournalSummary(Base):
    __tablename__ = "journal_summaries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
```

### Helper Functions

- `create_journal_summary(db, user_id, date, text)` - Creates and stores a summary
- `get_journal_summaries_for_user(db, user_id)` - Retrieves user's summaries

## API Endpoints

### Journal Summarization

**POST** `/journal/summarize`
```json
{
  "date": "2024-01-15",
  "text": "Journal entry text here..."
}
```

**Response**:
```json
{
  "id": "uuid",
  "user_id": "uuid", 
  "date": "2024-01-15",
  "summary_text": "AI-generated summary..."
}
```

### Get Journal Summaries

**GET** `/journal/summaries`

**Response**:
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "date": "2024-01-15", 
    "summary_text": "Summary text..."
  }
]
```

### AI Coach Insights

**GET** `/ai-insights`

**Response**:
```json
{
  "insights": "Personalized coaching recommendations..."
}
```

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_ai_functions.py
```

The test script includes:
- Journal summarization test with sample text
- AI coach insights test with sample data
- Error handling verification

## Error Handling

Both functions include comprehensive error handling:

1. **API Key Missing**: Returns appropriate error messages
2. **API Failures**: Graceful fallbacks or error messages
3. **Invalid Input**: Validation and error responses
4. **Network Issues**: Timeout handling and retry logic

## Configuration Options

### OpenAI Settings

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE`: API endpoint (supports local LLM endpoints)
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)

### Function Parameters

- **Temperature**: Controls creativity (0.3 for summaries, 0.4 for insights)
- **Max Tokens**: Limits response length
- **System Prompts**: Customizable behavior instructions

## Security Considerations

1. **API Key Security**: Store keys in environment variables
2. **Input Validation**: All user input is validated
3. **Rate Limiting**: Consider implementing rate limits for API calls
4. **Data Privacy**: Journal text is processed by OpenAI (review privacy policy)

## Performance Notes

- Journal summaries are cached in the database
- AI insights are generated on-demand
- Consider implementing caching for frequently requested insights
- Monitor API usage and costs

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured"**
   - Check your `.env` file
   - Verify environment variable is set

2. **"API call failed"**
   - Check network connectivity
   - Verify API key is valid
   - Check OpenAI service status

3. **"Model not found"**
   - Verify model name in configuration
   - Check if model is available in your OpenAI account

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Potential improvements:
- Support for local LLM models (Llama, etc.)
- Batch processing for multiple summaries
- Customizable prompt templates
- A/B testing for different coaching styles
- Integration with external wellness APIs 