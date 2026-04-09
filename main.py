from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None

items_db: dict[int, dict] = {}
next_id: int = 1

@app.get("/items", status_code=200)
def get_items():
    return items_db

@app.get("/items/{item_id}", status_code=200)
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.post("/items", status_code=201)
def create_item(item: Item):
    global next_id

    items_db[next_id] = item.model_dump()
    response = {"id": next_id, **items_db[next_id]}
    next_id += 1

    return response

@app.put("/items/{item_id}", status_code=200)
def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    items_db[item_id] = item.model_dump()
    return {"id": item_id, **items_db[item_id]}

@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = items_db.pop(item_id)
    return {"message": "Item deleted", "item": deleted_item}