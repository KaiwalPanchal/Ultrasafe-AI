import os
import uuid
import json
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel as LCBaseModel

# ---------------------------------------------------------------------------
# LangChain LLM configuration (UltraSafe backend)
# ---------------------------------------------------------------------------

ULTRASAFE_API_KEY: str | None = os.getenv("ULTRASAFE_API_KEY")
ULTRASAFE_API_BASE: str | None = os.getenv(
    "ULTRASAFE_API_BASE", "https://api.us.inc/usf/v1/hiring/chat/completions"
)

if not ULTRASAFE_API_KEY:
    raise RuntimeError("ULTRASAFE_API_KEY environment variable is not set")

llm = ChatOpenAI(
    model_name="usf1-mini",
    temperature=0.0,
    max_tokens=1000,
    openai_api_key=ULTRASAFE_API_KEY,
    openai_api_base=ULTRASAFE_API_BASE,
)

# ---------------------------------------------------------------------------
# Structured output definition
# ---------------------------------------------------------------------------


class EntityOut(LCBaseModel):
    text: str
    label: str


class EntitySchema(LCBaseModel):
    entities: List[EntityOut]


entity_chain = llm.with_structured_output(EntitySchema)

# ---------------------------------------------------------------------------
# FastAPI app & data models
# ---------------------------------------------------------------------------

app = FastAPI(title="NLP Entity Extraction API (Test A)")


class ExtractRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to extract entities from")
    webhook_url: Optional[str] = Field(
        None, description="Optional webhook URL for async notification"
    )


class Entity(BaseModel):
    text: str
    label: str


class ExtractResponse(BaseModel):
    id: str
    status: str
    results: Optional[List[List[Entity]]] = None


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


async def _post_webhook(url: str, payload: dict) -> None:
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=10)
        except Exception as exc:
            print(f"[WEBHOOK] Failed posting to {url}: {exc}")


def _extract_entities(texts: List[str]) -> List[List[Entity]]:
    results: List[List[Entity]] = []
    for t in texts:
        structured: EntitySchema = entity_chain.invoke(t)
        entities = [Entity(**e.dict()) for e in structured.entities]
        results.append(entities)
    return results


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------


@app.post("/extract-entities", response_model=ExtractResponse)
async def extract_entities(req: ExtractRequest, bg: BackgroundTasks):
    task_id = str(uuid.uuid4())

    if len(req.texts) > 50:
        raise HTTPException(status_code=400, detail="Batch size limit is 50 texts")

    if req.webhook_url:

        def _job():
            data = _extract_entities(req.texts)
            payload = {
                "id": task_id,
                "status": "completed",
                "results": json.loads(
                    json.dumps(data, default=lambda o: o.model_dump())
                ),
            }
            import anyio

            anyio.run(_post_webhook, req.webhook_url, payload)

        bg.add_task(_job)
        return ExtractResponse(id=task_id, status="processing")

    data = _extract_entities(req.texts)
    return ExtractResponse(id=task_id, status="completed", results=data)


@app.get("/")
async def root():
    return {"message": "UltraSafe Entity Extraction service running"}
