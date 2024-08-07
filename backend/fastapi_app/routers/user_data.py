from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 임시 저장소 (데이터베이스 대신 사용)
user_data_store = {
    "gender": None,
    "height": None,
    "weight": None,
    "brand": None
}

class UserDataRequest(BaseModel):
    gender: str
    height: float
    weight: float
    brand: str

@router.post("/save-user-data")
async def save_user_data(request: UserDataRequest):
    if request.gender not in ["남성", "여성"]:
        raise HTTPException(status_code=400, detail="Invalid gender")
    user_data_store["gender"] = request.gender
    user_data_store["height"] = request.height
    user_data_store["weight"] = request.weight
    user_data_store["brand"] = request.brand
    return {"message": "User data saved successfully"}

@router.get("/get-user-data")
async def get_user_data():
    if any(value is None for value in user_data_store.values()):
        raise HTTPException(status_code=404, detail="No complete user data found")
    return user_data_store
