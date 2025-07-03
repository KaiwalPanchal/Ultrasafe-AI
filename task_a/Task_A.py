"""
LangChain‑powered FastAPI micro‑service (custom LLM endpoint edition) - FIXED
=============================================================================

Endpoints
---------
POST /classify   → text classification
POST /extract    → named‑entity extraction (NER)
POST /summarize  → abstractive summarization
POST /sentiment  → sentiment analysis

Features
--------
* Accepts **single strings** or **lists** for batch processing.
* Fully **asynchronous**: uses modern LangChain LCEL + FastAPI async routes.
* Optional **webhook** notification: supply ``webhook_url`` in the request body and the
  service will immediately return 202‑style acknowledgment while a background task POSTs
  the results to your webhook when ready.
* **Caching**: Results are cached to improve performance for repeated requests.
* **Task Queuing**: Background task management for better resource utilization.
* Easily extensible—swap chains or plug a LangGraph graph for more complex agent flows.
* **Custom LLM endpoint**: works with *any* service exposing an OpenAI‑compatible
  chat‑completion route via ``base_url``—just set an environment variable.

Setup
-----
```bash
pip install fastapi uvicorn langchain-openai httpx langchain-core redis
export ULTRASAFE_API_KEY="your-api-key"
export ULTRASAFE_API_BASE="https://api.us.inc/usf/v1/hiring/chat/completions"
uvicorn langchain_api:app --reload
```

"""

from __future__ import annotations

import os
import asyncio
import json
import hashlib
import time
from typing import List, Union, Optional, Dict, Any
from functools import lru_cache

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ----------------------------------------------------------------------------
# Caching and Performance Configuration
# ----------------------------------------------------------------------------

# Simple in-memory cache (for production, use Redis)
class SimpleCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        self.cache.clear()

# Global cache instance
nlp_cache = SimpleCache(max_size=1000, ttl=3600)  # 1 hour TTL

def generate_cache_key(text: str, operation: str) -> str:
    """Generate a unique cache key for text and operation"""
    content = f"{operation}:{text.strip().lower()}"
    return hashlib.md5(content.encode()).hexdigest()

# ----------------------------------------------------------------------------
# LLM / Chain factory helpers
# ----------------------------------------------------------------------------

load_dotenv()

ULTRASAFE_API_KEY: str | None = os.getenv("ULTRASAFE_API_KEY")
ULTRASAFE_API_BASE: str | None = os.getenv(
    "ULTRASAFE_API_BASE", "https://api.us.inc/usf/v1/hiring/chat/completions"
)

if not ULTRASAFE_API_KEY:
    raise RuntimeError("ULTRASAFE_API_KEY environment variable is not set")


def _build_llm() -> ChatOpenAI:
    """Build LLM instance using UltraSafe configuration"""
    print(f"✅ Using LLM endpoint: {ULTRASAFE_API_BASE}")
    print(f"✅ Model: usf1-mini")
    print(f"✅ API key is set: {bool(ULTRASAFE_API_KEY)}")

    return ChatOpenAI(
        model_name="usf1-mini",
        temperature=0.0,
        max_tokens=1000,
        openai_api_key=ULTRASAFE_API_KEY,
        openai_api_base=ULTRASAFE_API_BASE,
        streaming=False,
    )


def _make_chain(prompt_template: str):
    """Create a modern LangChain chain using LCEL"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = _build_llm()
    parser = StrOutputParser()
    return prompt | llm | parser


# Improved Chains with better prompts ----------------------------------------

# Classification with clearer instructions and examples
classification_chain = _make_chain(
    """You are an expert text classifier. Your task is to classify the given text into ONE of the following categories:

CATEGORIES:
- technology: AI, software, hardware, programming, tech companies
- politics: government, elections, policy, politicians, political events
- sports: athletics, games, teams, players, competitions
- finance: stocks, markets, economy, banking, investments, business
- entertainment: movies, music, celebrities, TV shows, gaming
- health: medicine, wellness, fitness, healthcare, diseases
- education: schools, learning, research, academic topics
- travel: tourism, destinations, transportation, hotels
- food: cooking, restaurants, recipes, nutrition
- other: anything that doesn't fit the above categories

INSTRUCTIONS:
1. Read the text carefully
2. Identify the main topic and context
3. Choose the MOST relevant category from the list above
4. Respond with ONLY the category name (lowercase, no extra text)

Text: {text}

Category:"""
)

# Improved sentiment analysis with score
sentiment_chain = _make_chain(
    """You are a sentiment analysis expert. Analyze the sentiment of the given text and provide a numerical score.

SCORING SCALE:
- Score range: -100 to +100
- Negative scores (-100 to -1): negative sentiment (anger, sadness, criticism, disappointment)
- Zero (0): completely neutral sentiment
- Positive scores (+1 to +100): positive sentiment (happiness, satisfaction, praise, excitement)

SCORING GUIDELINES:
- -100 to -80: Extremely negative (hate, rage, severe criticism)
- -79 to -40: Very negative (strong dissatisfaction, clear negativity)
- -39 to -1: Mildly negative (slight criticism, minor complaints)
- 0: Completely neutral (factual, objective, no emotional tone)
- +1 to +39: Mildly positive (slight praise, minor satisfaction)
- +40 to +79: Very positive (clear happiness, strong approval)
- +80 to +100: Extremely positive (love, ecstasy, overwhelming praise)

INSTRUCTIONS:
1. Consider the overall emotional tone and context
2. Look for sentiment indicators like adjectives, adverbs, and emotional language
3. Consider implicit sentiment, not just explicit emotional words
4. If mixed sentiments exist, average them appropriately
5. Respond with ONLY the numerical score (integer between -100 and +100)

Text: {text}

Score:"""
)

# Enhanced NER with better structure and common entity types
ner_chain = _make_chain(
    """You are a Named Entity Recognition (NER) expert. Extract ALL named entities from the given text and classify them into appropriate types.

ENTITY TYPES:
- PERSON: People's names (first name, last name, full names)
- ORGANIZATION: Companies, institutions, government bodies, teams
- LOCATION: Cities, countries, states, addresses, landmarks
- DATE: Specific dates, years, months, time periods
- MONEY: Currency amounts, prices, financial values
- PRODUCT: Brand names, product names, models
- EVENT: Named events, conferences, holidays, disasters
- MISCELLANEOUS: Other important named entities not covered above

INSTRUCTIONS:
1. Identify all named entities in the text
2. For each entity, determine its most appropriate type from the list above
3. Include the exact text span as it appears in the original text
4. Output MUST be a valid JSON array where each element has 'entity' and 'type' keys
5. If no entities are found, return an empty array []
6. If you cannot format as JSON, return a simple list of entities separated by commas

Text: {text}

JSON:"""
)

# Improved summarization with better constraints
summary_chain = _make_chain(
    """You are a professional text summarizer. Create a concise, informative summary of the given text.

REQUIREMENTS:
1. Maximum 3 sentences
2. Capture the main points and key information
3. Use clear, professional language
4. Maintain factual accuracy
5. Avoid personal opinions or interpretations
6. Include important names, dates, and numbers if present

INSTRUCTIONS:
- Focus on the most important information
- Use active voice when possible
- Ensure the summary is self-contained and understandable
- Do not include unnecessary details or examples

Text: {text}

Summary:"""
)

# ----------------------------------------------------------------------------
# FastAPI application and data models
# ----------------------------------------------------------------------------
app = FastAPI(
    title="LangChain NLP API",
    version="2.0",
    description="Advanced NLP API with text classification, NER, summarization, and sentiment analysis",
)


class TextRequest(BaseModel):
    """Generic request body for all endpoints."""

    texts: Union[str, List[str]] = Field(
        ..., description="String or list of strings to process"
    )
    webhook_url: Optional[str] = Field(
        default=None,
        description=(
            "If provided, the endpoint responds immediately while a background "
            "task POSTs results to this URL upon completion."
        ),
    )

    def normalized_texts(self) -> List[str]:
        return self.texts if isinstance(self.texts, list) else [self.texts]


class ProcessingResponse(BaseModel):
    """Response model for successful processing."""

    results: List[Any]
    total_processed: int = Field(description="Number of texts processed")


class WebhookResponse(BaseModel):
    """Response model for webhook-enabled requests."""

    status: str
    detail: str
    webhook: str
    total_texts: int


# ----------------------------------------------------------------------------
# Task Queue and Async Processing
# ----------------------------------------------------------------------------

class TaskQueue:
    """Simple in-memory task queue for background processing"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.active_tasks = 0
        self.pending_tasks = []
        self.task_results = {}
    
    async def add_task(self, task_id: str, task_func, *args, **kwargs):
        """Add a task to the queue"""
        if self.active_tasks < self.max_concurrent:
            # Execute immediately
            self.active_tasks += 1
            try:
                result = await task_func(*args, **kwargs)
                self.task_results[task_id] = {"status": "completed", "result": result}
            except Exception as e:
                self.task_results[task_id] = {"status": "failed", "error": str(e)}
            finally:
                self.active_tasks -= 1
                # Process pending tasks
                if self.pending_tasks:
                    next_task = self.pending_tasks.pop(0)
                    asyncio.create_task(self.add_task(*next_task))
        else:
            # Queue for later execution
            self.pending_tasks.append((task_id, task_func, args, kwargs))
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        return self.task_results.get(task_id)

# Global task queue instance
task_queue = TaskQueue(max_concurrent=5)

# ----------------------------------------------------------------------------
# Async batch helpers with caching
# ----------------------------------------------------------------------------


async def _run_chain_batch(chain, texts: List[str], operation: str = "default") -> List[Any]:
    """Execute a LangChain chain asynchronously for a list of texts using modern LCEL with caching."""
    try:
        results = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cache_key = generate_cache_key(text, operation)
            cached_result = nlp_cache.get(cache_key)
            if cached_result is not None:
                results.append(cached_result)
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                results.append(None)  # Placeholder
        
        # Process uncached texts
        if uncached_texts:
            chain_results = await chain.abatch([{"text": text} for text in uncached_texts])
            
            for i, (text, result) in enumerate(zip(uncached_texts, chain_results)):
                result = result.strip() if isinstance(result, str) else str(result).strip()
                
                # Try to parse JSON for NER results
                if result.startswith("[") or result.startswith("{"):
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON
                
                # Cache the result
                cache_key = generate_cache_key(text, operation)
                nlp_cache.set(cache_key, result)
                
                # Update results list
                results[uncached_indices[i]] = result
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Chain processing failed: {str(e)}"
        )


async def _notify_webhook(url: str, payload: Dict[str, Any]) -> None:
    """POST payload to a webhook; swallow network errors to avoid crashing bg task."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            print(f"Webhook notification sent: {response.status_code}")
    except Exception as exc:  # proxy failures shouldn't crash server
        print(f"Webhook notification failed: {exc}")


async def _process_and_notify(chain, texts: List[str], webhook: str, operation: str = "default"):
    """Background task: run chain then notify webhook."""
    try:
        results = await _run_chain_batch(chain, texts, operation)
        await _notify_webhook(
            webhook,
            {
                "results": results,
                "total_processed": len(results),
                "status": "completed",
            },
        )
    except Exception as exc:
        await _notify_webhook(webhook, {"error": str(exc), "status": "failed"})


# ----------------------------------------------------------------------------
# Endpoint factory with improved error handling
# ----------------------------------------------------------------------------


def _register_endpoint(path: str, chain, endpoint_name: str):
    @app.post(path, response_model=Union[ProcessingResponse, WebhookResponse])
    async def _endpoint(request: TextRequest, background_tasks: BackgroundTasks):
        texts = request.normalized_texts()

        # Validate input
        if not texts or any(not text.strip() for text in texts):
            raise HTTPException(
                status_code=400, detail="All texts must be non-empty strings"
            )

        # Webhook mode -------------------------------------------------------
        if request.webhook_url:
            background_tasks.add_task(
                _process_and_notify, chain, texts, request.webhook_url, endpoint_name
            )
            return WebhookResponse(
                status="accepted",
                detail=f"Processing {len(texts)} text(s) asynchronously for {endpoint_name}.",
                webhook=request.webhook_url,
                total_texts=len(texts),
            )

        # Immediate mode -----------------------------------------------------
        try:
            results = await _run_chain_batch(chain, texts, endpoint_name)
            return ProcessingResponse(results=results, total_processed=len(results))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    # Set the endpoint name for better OpenAPI docs
    _endpoint.__name__ = f"{endpoint_name}_endpoint"
    return _endpoint


# Register routes with descriptive names ------------------------------------
_register_endpoint("/classify", classification_chain, "classification")
_register_endpoint("/sentiment", sentiment_chain, "sentiment_analysis")
_register_endpoint("/extract", ner_chain, "named_entity_recognition")
_register_endpoint("/summarize", summary_chain, "text_summarization")


# ----------------------------------------------------------------------------
# Health check and info endpoints
# ----------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "service": "LangChain NLP API (UltraSafe endpoint)",
        "version": "3.0",
        "endpoints": {
            "classification": "/classify",
            "sentiment_analysis": "/sentiment",
            "named_entity_recognition": "/extract",
            "text_summarization": "/summarize",
            "performance_metrics": "/performance",
            "cache_stats": "/cache/stats",
            "clear_cache": "/cache/clear",
        },
        "features": [
            "Batch processing",
            "Asynchronous webhook notifications",
            "UltraSafe LLM endpoint support",
            "Modern LangChain LCEL",
            "Result caching (1 hour TTL)",
            "Task queuing system",
            "Performance monitoring",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test LLM connection with a simple prompt
        llm = _build_llm()
        test_response = await llm.ainvoke("Test connection")
        return {
            "status": "healthy",
            "llm_model": "usf1-mini",
            "base_url": ULTRASAFE_API_BASE,
            "test_response_length": len(str(test_response)),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/performance")
async def performance_metrics():
    """Performance metrics endpoint for monitoring."""
    return {
        "cache": {
            "size": len(nlp_cache.cache),
            "max_size": nlp_cache.max_size,
            "hit_rate": "N/A",  # Would need to track hits/misses
        },
        "task_queue": {
            "active_tasks": task_queue.active_tasks,
            "pending_tasks": len(task_queue.pending_tasks),
            "max_concurrent": task_queue.max_concurrent,
            "completed_tasks": len(task_queue.task_results),
        },
        "system": {
            "uptime": "N/A",  # Would need to track start time
            "memory_usage": "N/A",  # Would need psutil
        }
    }


@app.post("/cache/clear")
async def clear_cache():
    """Clear the NLP cache."""
    nlp_cache.clear()
    return {"status": "success", "message": "Cache cleared"}


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return {
        "cache_size": len(nlp_cache.cache),
        "max_size": nlp_cache.max_size,
        "ttl_seconds": nlp_cache.ttl,
    }


# ----------------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "Task_A:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info",
    )
