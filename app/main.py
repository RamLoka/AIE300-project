from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

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

@app.get("/api")
def root():
    return {"message": "API is running"}

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
    result = await items_collection.insert_one(item.model_dump())

    new_item = await items_collection.find_one({"_id": result.inserted_id})

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
        item = await items_collection.find_one({"_id": ObjectId(item_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item_helper(item)

@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    try:
        result = await items_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": item.model_dump()}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    updated = await items_collection.find_one({"_id": ObjectId(item_id)})

    return item_helper(updated)

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    try:
        result = await items_collection.delete_one({"_id": ObjectId(item_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")