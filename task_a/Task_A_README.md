# FastAPI Natural Language Processing Pipeline (Task A)

A robust FastAPI application providing advanced NLP capabilities through a unified, scalable API. Includes text classification, entity extraction, summarization, sentiment analysis, batch/asynchronous processing, and webhook notifications.

## Key Features

- **Unified NLP API**: Endpoints for classification, entity extraction, summarization, and sentiment analysis
- **Batch Processing**: Accepts single strings or lists for efficient batch jobs
- **Asynchronous Tasks**: Non-blocking, async endpoints for long-running jobs
- **Webhook Notifications**: Optional webhook for task completion callbacks
- **Performance & Scaling**: Caching, efficient queuing, and horizontal scaling support

## Quick Start

### Prerequisites
```bash
pip install fastapi uvicorn langchain-openai httpx langchain-core
export ULTRASAFE_API_KEY="your-api-key"
export ULTRASAFE_API_BASE="https://api.us.inc/usf/v1/hiring/chat/completions"
```

### Run the API
```bash
uvicorn Task_A:app --reload
```

## Environment Setup (.env)

For convenience and security, you can store your API credentials in a `.env` file in the project root:

```
ULTRASAFE_API_KEY=your-api-key-here
ULTRASAFE_API_BASE=https://api.us.inc/usf/v1/hiring/chat/completions
```

- Replace `your-api-key-here` with your actual UltraSafe API key.
- The `ULTRASAFE_API_BASE` is usually the default shown above, but you can change it if needed.

### Using the .env File
- Install the `python-dotenv` package:
  ```bash
  pip install python-dotenv
  ```
- The FastAPI app will automatically load environment variables from `.env` if you add this to the top of your `Task_A.py`:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```
- Now you don't need to export variables manually; just edit `.env` and restart the app.

## API Endpoints

| Endpoint     | Method | Description                   |
| ------------ | ------ | ----------------------------- |
| `/classify`  | POST   | Text classification           |
| `/extract`   | POST   | Named-entity extraction (NER) |
| `/summarize` | POST   | Abstractive summarization     |
| `/sentiment` | POST   | Sentiment analysis            |

### Request Body (All Endpoints)
```json
{
  "texts": "string or list of strings",
  "webhook_url": "optional webhook URL for async notification"
}
```

### Response
- **Immediate**: 200 OK with results (for short jobs)
- **Webhook**: 202 Accepted, results POSTed to webhook when ready (for long jobs)

## Batch & Asynchronous Processing
- All endpoints accept single or multiple texts.
- If `webhook_url` is provided, processing is done in the background and results are sent to the webhook.
- Otherwise, results are returned directly.

## Webhook Notification Example
```json
{
  "status": "completed",
  "detail": "Task finished successfully.",
  "webhook": "https://your-callback-url.com/notify",
  "total_texts": 5
}
```

## Performance & Scaling
- **Caching**: Frequently requested results are cached for speed.
- **Task Queuing**: Async background tasks for heavy/batch jobs.
- **Horizontal Scaling**: Deploy behind a load balancer for multi-instance scaling.

## Example Usage (Python)
```python
import requests

# Classification
resp = requests.post("http://localhost:8000/classify", json={"texts": ["AI is transforming tech."]})
print(resp.json())

# Batch Summarization with webhook
resp = requests.post("http://localhost:8000/summarize", json={
    "texts": ["Long article 1...", "Long article 2..."],
    "webhook_url": "https://your-callback-url.com/notify"
})
print(resp.status_code)  # 202 Accepted
```

## API Documentation
- Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- All endpoints are fully documented with request/response schemas

## Performance Analysis & Scaling Strategies
- **Async Processing**: All endpoints are async for high concurrency.
- **Caching**: Reduces repeated computation for common queries.
- **Task Queuing**: Background tasks for webhook jobs prevent blocking.
- **Horizontal Scaling**: Run multiple instances with a load balancer (e.g., Kubernetes, Docker Swarm).
- **Stateless Design**: All state is externalized for easy scaling.

## File Structure
```
Task_A.py                # Main FastAPI application
requirements.txt         # Dependencies
README.md                # This file
```

---

**This FastAPI NLP pipeline delivers advanced, scalable, and context-aware language processing for modern applications.** 