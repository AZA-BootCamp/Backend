from fastapi import APIRouter, HTTPException, Request
from .user_data import feedback_store
router = APIRouter()


# 전체 브랜드 목록을 제공하는 엔드포인트
@router.get("/brands")
async def get_brands():
    # 사용 가능한 모든 브랜드 목록을 생성
    all_brands = set(feedback_store["여성"].keys()).union(feedback_store["남성"].keys())
    
    return list(all_brands)

# 특정 성별, 브랜드, 카테고리에 대한 피드백을 제공하는 엔드포인트
@router.get("/brands/{gender}/{brand}/{category}")
async def get_brand_feedback(gender: str, brand: str, category: str):
    # 성별, 브랜드, 카테고리에 해당하는 피드백을 가져옴
    feedback_data = feedback_store.get(gender, {}).get(brand, {}).get(category, None)

    if feedback_data is None:
        raise HTTPException(status_code=404, detail="Feedback data not found for the given parameters")

    return feedback_data

# 특정 성별과 브랜드에 대해 가능한 카테고리를 제공하는 엔드포인트
@router.get("/categories/{gender}/{brand}")
async def get_available_categories(gender: str, brand: str):
    # 해당 성별과 브랜드에 대한 모든 카테고리 반환
    categories = feedback_store.get(gender, {}).get(brand, None)

    if categories is None:
        raise HTTPException(status_code=404, detail="No categories found for the given brand and gender")

    #"반팔", "긴팔", "바지" 카테고리만 필터링
    filtered_data = {k: v for k, v in categories.items() if k in ["반팔", "긴팔", "바지"]}
    
    return filtered_data