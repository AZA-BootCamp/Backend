# 아이템 관련 엔드포인트를 위한 라우터
from fastapi import APIRouter, HTTPException
from models import Item
from crud import create_item, get_items, get_item, update_item, delete_item

router = APIRouter()

@router.post("/items")
async def create_item_endpoint(item: Item):
    create_item(item)
    return {"message": "Item created"}

@router.get("/items")
async def read_items():
    return get_items()

@router.get("/items/{item_id}")
async def read_item(item_id: str):
    item = get_item(item_id)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/items/{item_id}")
async def update_item_endpoint(item_id: str, item: Item):
    update_item(item_id, item)
    return {"message": "Item updated"}

@router.delete("/items/{item_id}")
async def delete_item_endpoint(item_id: str):
    delete_item(item_id)
    return {"message": "Item deleted"}
