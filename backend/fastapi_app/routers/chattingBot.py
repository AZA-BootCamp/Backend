from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import requests
import numpy as np

# Hugging Face API 엔드포인트와 API 키
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": "Bearer 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"}

# FastAPI 앱 인스턴스 생성
router = APIRouter()

# 데이터 클래스 정의
class QueryData(BaseModel):
    question: str

# 데이터 정의 (이전에 주어진 데이터 그대로 사용)
brands_data = [
    {
        "brand_name": "Zara",
        "target_audience": "20~30대 여성",
        "popular_products": [
            {
                "product_name": "Zara 플로럴 원피스",
                "category": "원피스",
                "season": "봄",
                "price": 79000,
                "popularity_rank": 1,
                "tags": ["데이트", "캐주얼", "봄"],
                "description": "봄철 데이트에 어울리는 우아한 플로럴 원피스입니다."
            },
            {
                "product_name": "Zara 하이웨이스트 진",
                "category": "바지",
                "season": "사계절",
                "price": 59000,
                "popularity_rank": 2,
                "tags": ["캐주얼", "데일리", "여름"],
                "description": "사계절 내내 편안하게 착용 가능한 하이웨이스트 진입니다."
            }
        ],
        "website_url": "https://www.zara.com",
        "description": "Zara는 트렌디한 패션을 선도하는 글로벌 브랜드입니다."
    },
    {
        "brand_name": "Adidas",
        "target_audience": "운동을 즐기는 사람들",
        "popular_products": [
            {
                "product_name": "Adidas 러닝화 Ultraboost",
                "category": "운동화",
                "season": "사계절",
                "price": 180000,
                "popularity_rank": 1,
                "tags": ["운동", "러닝", "트레이닝"],
                "description": "러닝과 트레이닝에 최적화된 Adidas의 최고급 러닝화입니다."
            },
            {
                "product_name": "Adidas 트랙수트",
                "category": "트레이닝복",
                "season": "가을",
                "price": 120000,
                "popularity_rank": 2,
                "tags": ["운동", "트레이닝", "가을"],
                "description": "가을철 운동에 적합한 편안한 트랙수트입니다."
            }
        ],
        "website_url": "https://www.adidas.com",
        "description": "Adidas는 세계적인 스포츠웨어 브랜드로, 다양한 운동용품을 제공합니다."
    },
    {
        "brand_name": "Polo",
        "target_audience": "30대 이상 남성",
        "popular_products": [
            {
                "product_name": "Polo 클래식 셔츠",
                "category": "셔츠",
                "season": "봄",
                "price": 110000,
                "popularity_rank": 1,
                "tags": ["비즈니스 캐주얼", "봄", "포멀"],
                "description": "봄철 비즈니스 캐주얼로 적합한 고급스러운 클래식 셔츠입니다."
            },
            {
                "product_name": "Polo 니트 스웨터",
                "category": "스웨터",
                "season": "겨울",
                "price": 150000,
                "popularity_rank": 2,
                "tags": ["겨울", "포멀", "캐주얼"],
                "description": "겨울철 따뜻하게 입을 수 있는 폴로 니트 스웨터입니다."
            }
        ],
        "website_url": "https://www.ralphlauren.com",
        "description": "Polo는 고급스러운 라이프스타일을 추구하는 남성 패션 브랜드입니다."
    }
]

# 데이터를 텍스트 리스트로 변환
data = []
for brand in brands_data:
    # 브랜드 설명 추가
    data.append(f"{brand['brand_name']} 브랜드: {brand['description']}")
    
    # 브랜드 인기 제품 설명 추가
    for product in brand['popular_products']:
        data.append(f"{brand['brand_name']} 브랜드의 인기 제품 {product['product_name']}: {product['description']} 가격은 {product['price']}원입니다.")
    
    # 브랜드 웹사이트 정보 추가
    data.append(f"{brand['brand_name']} 브랜드의 웹사이트는 {brand['website_url']} 입니다.")

# API 호출 함수: 텍스트를 임베딩으로 변환
def query_huggingface_api(source_sentence, sentences):
    payload = {
        "inputs": {
            "source_sentence": source_sentence,
            "sentences": sentences
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# POST 엔드포인트 - 쿼리 매개변수로 질문 받기
@router.post("/chatbot")
async def chatbot(question: str = Query(..., description="The question to ask the chatbot")):
    # Hugging Face API를 호출하여 유사도 계산
    result = query_huggingface_api(question, data)

    # API 응답을 확인하고 로그에 기록
    print(f"API 응답: {result}")  # 디버깅을 위한 API 응답 기록

    # 유사도가 가장 높은 문장 찾기
    if isinstance(result, list):
        closest_index = np.argmax(result)
        response_text = data[closest_index]
        return {"answer": response_text}
    else:
        raise HTTPException(status_code=500, detail="Unexpected response format from API")

