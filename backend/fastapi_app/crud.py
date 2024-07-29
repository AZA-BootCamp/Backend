# 데이터베이스 상호작용을 위한 기본적인 CRUD 함수 정의
from .database import db
from .models import Item

def create_item(item: Item):
    db.get_collection('items').insert_one(item.dict())

def get_items():
    return list(db.get_collection('items').find())

def get_item(item_id: str):
    return db.get_collection('items').find_one({"_id": item_id})

def update_item(item_id: str, item: Item):
    db.get_collection('items').update_one({"_id": item_id}, {"$set": item.dict()})

def delete_item(item_id: str):
    db.get_collection('items').delete_one({"_id": item_id})
