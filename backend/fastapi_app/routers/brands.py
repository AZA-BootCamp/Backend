from fastapi import APIRouter

router = APIRouter()

@router.get("/brands")
# 예시 데이터
async def get_brands():
    brands = ["Zara", "H&M", "Uniqlo", "Gap", "Levi's"]
    return brands
