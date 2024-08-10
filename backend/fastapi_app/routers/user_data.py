from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 임시 저장소 (데이터베이스 대신 사용)
user_data_store = {
    "gender": None,
    "height": None,
    "weight": None,
    "brand": None,
    "category":None,
}

# 피드백 데이터 저장소
feedback_store = {
    "여성": {
        "폴로랄프로렌": {
            "반팔": {"커요": "3%", "보통이에요": "95%", "작아요": "2%"},
            "긴팔": {"커요": "6%", "보통이에요": "93%", "작아요": "1%"},
            "바지": {"커요": "35%", "보통이에요": "65%"}
        },
        "아디다스": {
            "반팔": {"커요": "1%", "보통이에요": "94%", "작아요": "4%"},
            "긴팔": {"커요": "5%", "보통이에요": "95%"},
            "바지": {"커요": "10%", "보통이에요": "90%"}
        },
        "나이키": {
            "반팔": {"커요": "16%", "보통이에요": "82%", "작아요": "3%"},
            "긴팔": {"커요": "20%", "보통이에요": "80%"},
            "바지": {"보통이에요": "84%", "작아요": "16"}
        },
        "Tommy hilfiger": {
            "반팔": {"보통이에요": "100%"},
            "긴팔": {"보통이에요": "100%"},
            "바지": {"커요": "17%", "보통이에요": "83%"}
        },
        "캘빈클라인": {
            "반팔": {"커요": "32%", "보통이에요": "67%"},
            "긴팔": {"보통이에요": "86%", "작아요": "14%"},
            "바지": {"커요": "7%", "보통이에요": "90%", "작아요": "3%"}
        },
        "saint laurent": {
            "반팔": {"커요": "%", "보통이에요": "86%", "작아요": "14%"},
            "긴팔": { "보통이에요": "90%", "작아요": "10%"},
            "바지": {"커요": "6%", "보통이에요": "92%", "작아요": "2%"}
        },
        "ami": {
            "반팔": {"커요": "50%", "보통이에요": "50%"},
            "긴팔": {"커요": "8%", "보통이에요": "85%", "작아요": "8%"},
        },
        "kenzo": {
            "반팔": {"커요": "30%", "보통이에요": "70%"},
            "긴팔": {"커요": "30%", "보통이에요": "70%"},
            "바지": {"보통이에요": "82%", "작아요": "18%"}
        },
        "메종키츠네": {
            "반팔": {"커요": "5%", "보통이에요": "95%"},
            "긴팔": {"보통이에요": "100%"},
            "바지": {"커요": "5%", "보통이에요": "95%"}
        },
    },
    "남성": {
        "폴로랄프로렌": {
            "반팔": {"커요": "3%", "보통이에요": "92%", "작아요": "5%"},
            "긴팔": {"커요": "20%", "보통이에요": "75%", "작아요": "5%"},
            "바지": {"커요": "16%", "보통이에요": "81%", "작아요": "2%"}
        },
        "아디다스": {
            "반팔": {"커요": "31%", "보통이에요": "69%"},
            "긴팔": {"커요": "22%", "보통이에요": "72%", "작아요": "6%"},
            "바지": {"커요": "25%", "보통이에요": "75%"}
        },
        "나이키": {
            "반팔": {"커요": "12%", "보통이에요": "88%"},
            "긴팔": {"커요": "14%", "보통이에요": "86%"},
            "바지": {"커요": "5%", "보통이에요": "92%", "작아요": "4%"}
        },
        "Tommy hilfiger": {
            "반팔": {"보통이에요": "100%"},
            "긴팔": {"커요": "46%", "보통이에요": "54%"},
            "바지": {"보통이에요": "100%"}
        },
        "캘빈클라인": {
            "반팔": {"커요": "32%", "보통이에요": "67%"},
            "긴팔": {"커요": "8%", "보통이에요": "88%", "작아요": "5%"},
        },
        "saint laurent": {
            "반팔": {"커요": "%", "보통이에요": "86%", "작아요": "14%"},
            "긴팔": { "보통이에요": "92%", "작아요": "8%"},
        },
        "ami": {
            "반팔": {"커요": "50%", "보통이에요": "50%"},
            "긴팔": {"커요": "27%", "보통이에요": "70%", "작아요": "3%"},
            "바지": {"보통이에요": "100%"}
        },
        "kenzo": {
            "반팔": {"커요": "30%", "보통이에요": "70%"},
            "긴팔": {"커요": "10%", "보통이에요": "90%"},
            "바지": {"커요": "50%", "보통이에요": "50%"}
        },
        "메종키츠네": {
            "반팔": {"커요": "5%", "보통이에요": "95%"},
            "긴팔": {"커요": "17%", "보통이에요": "83%"},
            "바지": {"커요": "10%", "보통이에요": "90%"}
        },
    }
}

class UserDataRequest(BaseModel):
    gender: str
    height: float
    weight: float
    brand: str
    category: str


class UserDataRequest(BaseModel):
    gender: str
    height: float
    weight: float
    brand: str
    category: str


@router.post("/save-user-data")
async def save_user_data(request: UserDataRequest):
    if request.gender not in ["남성", "여성"]:
        raise HTTPException(status_code=400, detail="Invalid gender")
    user_data_store["gender"] = request.gender
    user_data_store["height"] = request.height
    user_data_store["weight"] = request.weight
    user_data_store["brand"] = request.brand
    user_data_store["category"] = request.category
    return {"message": "User data saved successfully"}

@router.get("/get-user-data")
async def get_user_data():
    if any(value is None for value in user_data_store.values()):
        raise HTTPException(status_code=404, detail="No complete user data found")
    return user_data_store

@router.post("/get-user-feedback")
async def get_user_feedback():
    # 저장된 사용자 데이터를 가져옵니다
    user_data = user_data_store

    # 가져온 사용자 데이터로 피드백 조회
    feedback_data = feedback_store.get(user_data['gender'], {}).get(user_data['brand'], {}).get(user_data['category'], None)

    if feedback_data is None:
        raise HTTPException(status_code=404, detail="Feedback data not found for the user's data")

    return feedback_data
