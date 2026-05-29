from openai import OpenAI
import requests, json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.database import collection as items_collection
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[dict] = []

class ChatResponse(BaseModel):
    reply: str
    conversation_history: List[dict]

class AnalyzeRequest(BaseModel):
    content: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant for a student project app. "
                "Be concise, clear, and helpful."
            )
        }
    ]

    messages.extend(request.conversation_history)

    messages.append({
        "role": "user",
        "content": request.message
    })

    try:

        response = client.chat.completions.create(
            model="llama3",
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        updated_history = request.conversation_history + [
            {
                "role": "user",
                "content": request.message
            },
            {
                "role": "assistant",
                "content": reply
            }
        ]

        return ChatResponse(
            reply=reply,
            conversation_history=updated_history
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )

@app.post("/analyze")
def analyze(request: AnalyzeRequest):

    system_prompt = """
You are an item analysis assistant.

Analyze the provided item description and respond with ONLY valid JSON
in this exact format:

{
    "categories": ["category1", "category2"],
    "tags": ["tag1", "tag2", "tag3"],
    "sentiment": "positive" | "negative" | "neutral",
    "summary": "one sentence summary"
}

Rules:
- Return ONLY valid JSON
- No markdown
- No explanations
- No extra text
"""

    few_shot = """
Example:

Input:
"This gaming laptop is extremely fast, lightweight, and has amazing battery life."

Output:
{
    "categories": ["technology", "electronics"],
    "tags": ["gaming", "laptop", "battery", "performance"],
    "sentiment": "positive",
    "summary": "Positive review of a high-performance gaming laptop."
}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content":
                few_shot +
                "\n\nNow analyze this:\n" +
                request.content
        }
    ]

    try:

        response = client.chat.completions.create(
            model="llama3",
            messages=messages,
            max_tokens=512,
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()

        start = raw.find("{")
        end = raw.rfind("}") + 1

        if start != -1 and end != -1:
            raw = raw[start:end]

        try:

            result = json.loads(raw)

        except json.JSONDecodeError:

            retry_messages = messages + [
                {
                    "role": "assistant",
                    "content": raw
                },
                {
                    "role": "user",
                    "content":
                        "Return ONLY valid JSON."
                }
            ]

            retry_response = client.chat.completions.create(
                model="llama3",
                messages=retry_messages,
                max_tokens=512,
                temperature=0.1
            )

            raw = retry_response.choices[0].message.content.strip()

            start = raw.find("{")
            end = raw.rfind("}") + 1

            if start != -1 and end != -1:
                raw = raw[start:end]

            result = json.loads(raw)

        required = [
            "categories",
            "tags",
            "sentiment",
            "summary"
        ]

        for field in required:

            if field not in result:

                raise ValueError(
                    f"Missing field: {field}"
                )

        return result

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=422,
            detail="LLM returned invalid JSON."
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api")
def root():
    return {"message": "API is running"}

@app.post("/predict")
def predict(data: dict):

    response = requests.post(
        "http://model-service:8001/predict",
        json={"features": data["features"]}
    )

    return response.json()

class Item(BaseModel):
    name: str
    description: Optional[str] = None

def item_helper(item) -> dict:

    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item.get("description"),
    }

@app.post("/items", status_code=201)
async def create_item(item: Item):

    result = await items_collection.insert_one(
        item.model_dump()
    )

    new_item = await items_collection.find_one(
        {"_id": result.inserted_id}
    )

    return item_helper(new_item)

@app.get("/items")
async def get_items():

    items = []

    async for item in items_collection.find():
        items.append(item_helper(item))

    return items

@app.get("/items/{item_id}")
async def get_item(item_id: str):

    try:

        item = await items_collection.find_one(
            {"_id": ObjectId(item_id)}
        )

    except:

        raise HTTPException(
            status_code=400,
            detail="Invalid ID format"
        )

    if not item:

        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item_helper(item)

@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):

    try:

        result = await items_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": item.model_dump()}
        )

    except:

        raise HTTPException(
            status_code=400,
            detail="Invalid ID format"
        )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    updated = await items_collection.find_one(
        {"_id": ObjectId(item_id)}
    )

    return item_helper(updated)

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):

    try:

        result = await items_collection.delete_one(
            {"_id": ObjectId(item_id)}
        )

    except:

        raise HTTPException(
            status_code=400,
            detail="Invalid ID format"
        )

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return {"message": "Item deleted"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")