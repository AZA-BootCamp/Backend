from fastapi import APIRouter, HTTPException, Request
router = APIRouter()


# 전체 브랜드 목록을 제공하는 엔드포인트
@router.get("/measurement")
async def get_brands():
    # 사용 가능한 모든 브랜드 목록을 생성
    all_brands = "a"
    
    return  all_brands
