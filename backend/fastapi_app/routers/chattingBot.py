from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import requests
import numpy as np
import random

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
        "brand_name": "Polo Ralph Lauren",
        "target_audience": "30대 이상 남성",
        "popular_products": [
        {
            "product_name": "Classic Fit Oxford Shirt",
            "category": "셔츠",
            "season": "봄/가을",
            "price": 155000,
            "popularity_rank": 1,
            "tags": ["캐주얼", "비즈니스 캐주얼", "포멀"],
            "description": "일상적인 비즈니스 캐주얼이나 데일리 룩에 적합한 클래식한 스타일의 셔츠입니다.",
            "gender": "female"
        },
        {
            "product_name": "Relaxed Fit Linen Shirt",
            "category": "셔츠",
            "season": "여름",
            "price": 175000,
            "popularity_rank": 2,
            "tags": ["여름", "캐주얼", "데일리"],
            "description": "더운 여름철에 시원하게 입을 수 있는 린넨 셔츠로, 캐주얼한 일상에 적합합니다.",
            "gender": "female"
        },
        {
            "product_name": "High-Rise Wide-Leg Pants",
            "category": "바지",
            "season": "사계절",
            "price": 225000,
            "popularity_rank": 1,
            "tags": ["포멀", "비즈니스 캐주얼", "데일리"],
            "description": "세련된 디자인으로, 비즈니스 캐주얼이나 포멀한 자리에서 입기 좋은 바지입니다.",
            "gender": "female"
        },
        {
            "product_name": "Slim Fit Stretch Pants",
            "category": "바지",
            "season": "봄/가을",
            "price": 198000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "데일리", "편안함"],
            "description": "신축성이 좋아 편안하면서도 스타일리시하게 입을 수 있는 슬림 핏 바지입니다.",
            "gender": "female"
        },
        {
            "product_name": "커스텀 핏 옥스포드 셔츠",
            "category": "셔츠",
            "season": "사계절",
            "price": 150000,
            "popularity_rank": 1,
            "tags": ["캐주얼", "비즈니스 캐주얼", "포멀"],
            "description": "클래식한 디자인과 편안한 핏이 돋보이는 셔츠로, 다양한 상황에 적합합니다.",
            "gender": "male"
        },
        {
            "product_name": "슬림핏 스트레치 셔츠",
            "category": "셔츠",
            "season": "봄/여름",
            "price": 130000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "데일리", "경량"],
            "description": "슬림한 핏과 스트레치 소재로 편안함을 더한 셔츠입니다.",
            "gender": "male"
        },
        {
            "product_name": "커스텀 슬림 스트레이트 데님",
            "category": "바지",
            "season": "사계절",
            "price": 180000,
            "popularity_rank": 1,
            "tags": ["캐주얼", "데일리", "모던"],
            "description": "편안하면서도 스타일리시한 데님 팬츠로, 데일리 룩에 적합합니다.",
            "gender": "male"
        },
        {
            "product_name": "스트레치 치노 팬츠",
            "category": "바지",
            "season": "봄/가을",
            "price": 160000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "비즈니스 캐주얼", "편안함"],
            "description": "편안한 착용감과 깔끔한 실루엣을 제공하는 치노 팬츠입니다.",
            "gender": "male"
        }
        ],
        "website_url": "https://www.ralphlauren.com",
        "description": "고급스러운 라이프스타일을 선도하는"
    },
    {
        "brand_name": "Adidas",
        "target_audience": "운동을 즐기는 사람들",
        "popular_products": [
        {
            "product_name": "Adidas 여성용 머스트해브 3-스트라이프 티",
            "category": "셔츠",
            "season": "사계절",
            "price": 30000,
            "popularity_rank": 1,
            "tags": ["캐주얼", "데일리 웨어", "스포츠"],
            "description": "편안함과 아이코닉한 3-스트라이프 디자인이 결합된 다용도 티셔츠로, 일상적인 캐주얼 웨어 또는 가벼운 운동에 적합합니다.",
            "gender": "female"
        },
        {
            "product_name": "Adidas 에센셜스 리니어 로고 티",
            "category": "셔츠",
            "season": "여름",
            "price": 25000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "여름", "경량"],
            "description": "이 경량 티셔츠는 더운 여름날에 이상적이며, 통기성이 뛰어나고 클래식한 아디다스 로고가 돋보입니다.",
            "gender": "female"
        },
        {
            "product_name": "Adidas 티로 21 트레이닝 팬츠",
            "category": "바지",
            "season": "가을/겨울",
            "price": 45000,
            "popularity_rank": 1,
            "tags": ["트레이닝", "스포츠", "편안함"],
            "description": "이 팬츠는 트레이닝 세션을 위해 디자인되었으며, 추운 계절에도 편안함과 유연성을 제공합니다.",
            "gender": "female"
        },
        {
            "product_name": "Adidas 3-스트라이프 레깅스",
            "category": "바지",
            "season": "사계절",
            "price": 40000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "운동", "스타일리시"],
            "description": "스타일리시하면서도 기능적인 이 레깅스는 캐주얼 웨어와 운동 활동에 모두 적합합니다.",
            "gender": "female"
        },
        {
            "product_name": "Adidas 에어로레디 티셔츠",
            "category": "셔츠",
            "season": "사계절",
            "price": 45000,
            "popularity_rank": 1,
            "tags": ["운동", "데일리", "캐주얼"],
            "description": "사계절 내내 착용 가능한 통기성이 좋은 티셔츠로, 운동과 데일리 룩에 적합합니다.",
            "gender": "male"
        },
        {
            "product_name": "Adidas 에센셜 3-스트라이프 티",
            "category": "셔츠",
            "season": "봄/여름",
            "price": 35000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "경량", "데일리"],
            "description": "봄과 여름철에 적합한 경량 티셔츠로, 캐주얼하고 편안한 스타일입니다.",
            "gender": "male"
        },
        {
            "product_name": "Adidas 티로 21 트레이닝 팬츠",
            "category": "바지",
            "season": "가을/겨울",
            "price": 60000,
            "popularity_rank": 1,
            "tags": ["운동", "트레이닝", "편안함"],
            "description": "가을과 겨울에 편안하게 착용할 수 있는 트레이닝 팬츠로, 운동에 최적화되어 있습니다.",
            "gender": "male"
        },
        {
            "product_name": "Adidas 프라임그린 테이퍼드 팬츠",
            "category": "바지",
            "season": "사계절",
            "price": 55000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "비즈니스 캐주얼", "지속 가능성"],
            "description": "지속 가능한 소재로 제작된 팬츠로, 사계절 내내 착용하기 적합하며, 캐주얼과 비즈니스 캐주얼에 잘 어울립니다.",
            "gender": "male"
        },
        ],
        "website_url": "https://www.adidas.com",
        "description": "혁신적인 디자인과 기술로 스포츠웨어를 선도하는"
    },
    {
        "brand_name": "Nike",
        "target_audience": "모든 연령대의 운동 애호가들",
        "popular_products": [
        {
            "product_name": "Nike Sportswear Club Fleece 풀오버 후디",
            "category": "셔츠",
            "season": "가을/겨울",
            "price": 65000,
            "popularity_rank": 1,
            "tags": ["캐주얼", "편안함", "따뜻함"],
            "description": "부드럽고 따뜻한 플리스 소재로 제작되어 추운 날씨에도 편안하게 착용할 수 있는 후디입니다.",
            "gender": "male"
        },
        {
            "product_name": "Nike Dri-FIT ADV 테크 플리스 런닝 탑",
            "category": "셔츠",
            "season": "사계절",
            "price": 80000,
            "popularity_rank": 2,
            "tags": ["운동", "런닝", "통기성"],
            "description": "통기성이 뛰어나고 땀을 빠르게 흡수하는 Dri-FIT 기술이 적용된 탑으로, 모든 계절에 적합한 운동용 셔츠입니다.",
            "gender": "male"
        },
        {
            "product_name": "Nike Sportswear Tech Fleece 조거 팬츠",
            "category": "바지",
            "season": "사계절",
            "price": 106970,
            "popularity_rank": 1,
            "tags": ["편안함", "캐주얼", "데일리"],
            "description": "사계절 내내 편안하게 착용할 수 있는 테크 플리스 조거 팬츠로, 캐주얼한 스타일링에 적합합니다.",
            "gender": "male"
        },
        {
            "product_name": "Nike Sportswear Club 코듀로이 치노 팬츠",
            "category": "바지",
            "season": "가을/겨울",
            "price": 95000,
            "popularity_rank": 2,
            "tags": ["비즈니스 캐주얼", "따뜻함", "편안함"],
            "description": "고급스러운 코듀로이 소재로 만들어진 치노 팬츠로, 가을과 겨울철의 비즈니스 캐주얼 룩에 잘 어울립니다.",
            "gender": "male"
        },
        {
            "product_name": "Nike Sportswear Essential Women's T-Shirt",
            "category": "셔츠",
            "season": "사계절",
            "price": 40000,
            "popularity_rank": 1,
            "tags": ["캐주얼", "데일리", "기본"],
            "description": "데일리 룩으로 완벽한 기본 티셔츠로, 편안한 착용감과 다양한 컬러로 사계절 내내 입기 좋습니다.",
            "gender": "female"
        },
        {
            "product_name": "Nike One Classic Women's Dri-FIT Short-Sleeve Top",
            "category": "셔츠",
            "season": "여름",
            "price": 50000,
            "popularity_rank": 2,
            "tags": ["운동", "여름", "쿨링"],
            "description": "여름철 운동에 최적화된 쿨링 기능을 갖춘 Dri-FIT 소재의 셔츠로, 운동 시 시원함을 제공합니다.",
            "gender": "female"
        },
        {
            "product_name": "Nike Sportswear Tech Fleece Women's Joggers",
            "category": "바지",
            "season": "가을/겨울",
            "price": 120000,
            "popularity_rank": 1,
            "tags": ["운동", "트레이닝", "편안함"],
            "description": "추운 날씨에 적합한 따뜻한 Tech Fleece 소재로 제작된 조거 팬츠로, 운동 및 트레이닝에 적합합니다.",
            "gender": "female"
        },
        {
            "product_name": "Nike Sportswear Club Fleece Women's Mid-Rise Sweatpants",
            "category": "바지",
            "season": "사계절",
            "price": 70000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "데일리", "편안함"],
            "description": "사계절 내내 편안하게 착용할 수 있는 플리스 소재의 미드라이즈 팬츠로, 캐주얼한 일상에 잘 어울립니다.",
            "gender": "female"
        }
        ],
        "website_url": "https://www.nike.com",
        "description": "전 세계적으로 가장 영향력 있는"
    },
    {
        "brand_name": "Tommy Hilfiger",
        "target_audience": "모든 연령대의 클래식 패션 애호가들",
        "popular_products": [
            {
            "product_name": "Stretch Regular Fit Tommy Polo",
            "category": "셔츠",
            "season": "사계절",
            "price": 48700,
            "popularity_rank": 1,
            "tags": ["캐주얼", "비즈니스 캐주얼", "편안함"],
            "description": "이 스트레치 레귤러 핏 폴로 셔츠는 편안함과 활동성을 위해 신축성 있는 소재로 제작되었습니다. 다양한 색상으로 제공되며, 캐주얼과 세미 포멀 스타일에 잘 어울립니다.",
            "gender": "male"
        },
        {
            "product_name": "1985 Slim Fit Polo",
            "category": "셔츠",
            "season": "사계절",
            "price": 34900,
            "popularity_rank": 2,
            "tags": ["캐주얼", "포멀", "지속 가능성"],
            "description": "1985 컬렉션의 슬림 핏 폴로는 지속 가능한 소재로 제작되었으며, 모던한 핏을 자랑합니다. 다양한 색상 옵션이 있으며, 스타일리시하면서도 환경을 생각한 선택입니다.",
            "gender": "male"
        },
        {
            "product_name": "THFlex Slim Fit Tommy Chino",
            "category": "바지",
            "season": "사계절",
            "price": 47700,
            "popularity_rank": 1,
            "tags": ["캐주얼", "비즈니스 캐주얼", "편안함"],
            "description": "이 슬림 핏 치노 바지는 편안함과 스타일을 동시에 제공하며, 캐주얼 및 비즈니스 캐주얼 스타일에 적합한 필수 아이템입니다.",
            "gender": "male"
        },
        {
            "product_name": "Relaxed Tapered Fit Cargo Pant",
            "category": "바지",
            "season": "사계절",
            "price": 90300,
            "popularity_rank": 2,
            "tags": ["캐주얼", "실용성", "편안함"],
            "description": "이 릴렉스드 테이퍼드 핏 카고 팬츠는 실용적이며, 편안한 핏을 자랑합니다. 다양한 포켓이 있어 일상 및 야외 활동에 적합합니다.",
            "gender": "male"
        },
        {
            "product_name": "깅엄 체크 미디 셔츠 원피스",
            "category": "원피스",
            "season": "봄/가을",
            "price": 192500,
            "popularity_rank": 1,
            "tags": ["단정함", "데일리", "편안함"],
            "description": "100% 코튼 소재의 셔츠형 드레스로 더위를 식히기 좋고, 활동하기 편안한 깅엄패턴이 매력적인 깅엄 미디 셔츠 드레스입니다.",
            "gender": "female"
        },
        {
            "product_name": "플리츠 미디 원피스",
            "category": "원피스",
            "season": "봄/여름/가을",
            "price": 255000,
            "popularity_rank": 2,
            "tags": ["캐주얼", "세련됨", "편안함"],
            "description": "골지 소재의 숏 슬리브와 찰랑거리는 플리츠 소재가 페미닌한 무드를 자아내는 드레스입니다.",
            "gender": "female"
        }
        ],
        "website_url": "https://www.tommy.com",
        "description": "클래식한 아메리칸 스타일을 대표하는"
    },
    {
        "brand_name": "Calvin Klein",
        "target_audience": "모던하고 심플한 스타일을 선호하는 사람들",
        "popular_products": [
            {
                "product_name": "남성 릴렉스핏 아카이브 로고 반팔 티셔츠",
                "category": "티셔츠",
                "season": "봄/여름/가을",
                "price": 59000,
                "popularity_rank": 1,
                "tags": ["편안함", "데일리", "심플"],
                "description": "왼쪽 가슴의 미니멀한 CK 모노그램 로고가 포인트입니다.",
                "gender": "male"
            },
            {
                "product_name": "남성 90'S 오로라 블루 데님 자켓",
                "category": "자켓",
                "season": "봄/가을",
                "price": 299000,
                "popularity_rank": 2,
                "tags": ["데님", "데일리", "심플"],
                "description": "클래식한 디자인의 데님 자켓으로, 오로라 디자인의 워시가 특징입니다.",
                "gender": "male"

            },
            {
                "product_name": "남성 스탠다드 스트레이트핏 린스블루 데님",
                "category": "바지",
                "season": "사계절",
                "price": 229000,
                "popularity_rank": 2,
                "tags": ["데님", "데일리", "심플"],
                "description": "클린한 린스블루 워시와 로고 가죽 패치, 포켓 로고 라벨 디자인이 포인트입니다.",
                "gender": "male"
            },
            {
                "product_name": "남성 슬림 드로우코드 치노 팬츠",
                "category": "바지",
                "season": "사계절",
                "price": 229000,
                "popularity_rank": 2,
                "tags": ["슬림핏", "데일리", "심플"],
                "description": "투웨이 스트레치 트윌 소재로 제작된 슬림 드로우코드 치노 팬츠입니다. 데일리로 활용하기 좋은 클래식한 디자인입니다.",
                "gender": "male"
            },
            {
                "product_name": "여성 모노그램 로고 뱃지 폴로 카라 립 원피스",
                "category": "원피스",
                "season": "봄/여름/가을",
                "price": 199000,
                "popularity_rank": 1,
                "tags": ["포멀", "데일리", "심플"],
                "description": "라이크라 소재 함유로 부드러운 핸드필의 폴로 칼라의 립 드레스입니다.",
                "gender": "female"
            },
            {
                "product_name": "여성 모노그램 로고 뱃지 폴로 카라 립 원피스",
                "category": "원피스",
                "season": "봄/여름/가을",
                "price": 199000,
                "popularity_rank": 1,
                "tags": ["포멀", "데일리", "심플"],
                "description": "라이크라 소재 함유로 부드러운 핸드필의 폴로 칼라의 립 드레스입니다.",
                "gender": "female"
            },
            {
                "product_name": "여성볼레로 가디건 슬리브리스 니트 탑세트",
                "category": "니트",
                "season": "봄/여름/가을",
                "price": 199000,
                "popularity_rank": 2,
                "tags": ["귀여움", "데일리", "가벼움"],
                "description": "벌룬 쉐입의 소매로 귀여운 느낌 연출 가능하며 탑 가슴 중앙의 ck로고가 포인트입니다.",
                "gender": "female"
            },
            {
                "product_name": "여성 로우라이즈 스트레이트핏 블랙 데님",
                "category": "바지",
                "season": "사계절",
                "price": 249000,
                "popularity_rank": 1,
                "tags": ["심플", "시크", "데일리"],
                "description": "블랙워시이며 클린한 디자인으로 다양한 데일리 코디에 활용 가능한 제품입니다.",
                "gender": "female"
            },
            {
                "product_name": "여성 로우라이즈 배기핏 카고 미드블루 데님",
                "category": "바지",
                "season": "사계절",
                "price": 269000,
                "popularity_rank": 2,
                "tags": ["심플", "캐주얼", "데일리"],
                "description": "배기핏과 카고 디테일로 포인트를 준 제품입니다.",
                "gender": "female"
            },
        ],
        "website_url": "https://www.calvinklein.com",
        "description": "모던하고 미니멀한 디자인으로 전 세계적으로 사랑받는"
    },
    {
        "brand_name": "Saint Laurent",
        "target_audience": "고급스러운 패션을 추구하는 사람들",
        "popular_products": [
            {
                "product_name": "울 개버딘 소재의 재킷",
                "category": "자켓",
                "season": "사계절",
                "price": 4520000,
                "popularity_rank": 1,
                "tags": ["캐주얼", "포멀", "지속 가능성"],
                "description": "럭셔리 패션의 정수를 보여주는 Saint Laurent의 울 재킷입니다.",
                "gender": "female"
            },
            {
                "product_name": "실크 새틴 소재의 V 넥 드레스",
                "category": "원피스",
                "season": "봄",
                "price": 6360000,
                "popularity_rank": 2,
                "tags": ["럭셔리", "우아함", "화려함"],
                "description": "고급스러움과 우아함을 겸비한 Saint Laurent의 V넥 드레스입니다.",
                "gender": "female"
            },
            {
                "product_name": "실크 크레이프 소재의 재킷",
                "category": "자켓",
                "season": "봄/여름/가을",
                "price": 5860000,
                "popularity_rank": 1,
                "tags": ["캐주얼", "포멀", "시크"],
                "description": "럭셔리 패션의 정수를 보여주는 Saint Laurent의 실크 크레이프 소재 재킷입니다.",
                "gender": "male"
            },
            {
                "product_name": "샤를로트 블루 데님 소재의 롱 배기 진",
                "category": "바지",
                "season": "사계절",
                "price": 1430000,
                "popularity_rank": 2,
                "tags": ["캐주얼", "포멀", "데일리"],
                "description": "럭셔리 패션의 정수를 보여주는 Saint Laurent의 샤플로트 블루 데님 소재의 진입니다.",
                "gender": "male"
            },
        ],
        "website_url": "https://www.ysl.com",
        "description": "세계적인 럭셔리, 고급 패션의 대명사인"
    },
    {
        "brand_name": "Kenzo",
        "target_audience": "개성 있고 독창적인 스타일을 선호하는 사람들",
        "popular_products": [
            {
                "product_name": "'KENZO Constellation' 엠브로이드 KIMONO",
                "category": "자켓",
                "season": "사계절",
                "price": 1034000,
                "popularity_rank": 1,
                "tags": ["개성", "독창적", "스트리트"],
                "description": "가슴과 뒷면에 Kenzo의 독창적인 자수가 있는 자켓입니다.",
                "gender": "male"
            },
            {
                "product_name": "'KENZO Jungle heart' 가디건",
                "category": "가디건",
                "season": "봄/가을",
                "price": 792000,
                "popularity_rank": 2,
                "tags": ["개성", "독창적", "스트리트"],
                "description": "Kenzo의 독창적인 디자인이 특징인 가디건입니다.",
                "gender": "male"
            },
            {
                "product_name": "'KENZO Jungle Heart' 엠브로이드리 윈드브레이커",
                "category": "윈드브레이커",
                "season": "봄/가을",
                "price": 858000,
                "popularity_rank": 1,
                "tags": ["개성", "독창적", "스트리트"],
                "description": "Kenzo의 독창적인 디자인이 특징인 윈드브레이커입니다.",
                "gender": "female"
            },
            {
                "product_name": "'KENZO Jungle Heart' 엠브로이드 클래식 티셔츠",
                "category": "티셔츠",
                "season": "봄/여름/가을",
                "price": 264000,
                "popularity_rank": 2,
                "tags": ["개성", "독창적", "스트리트"],
                "description": "Kenzo의 독창적인 디자인이 특징인 클래식 티셔츠입니다.",
                "gender": "female"
            }
        ],
        "website_url": "https://www.kenzo.com",
        "description": "대담하고 혁신적인 디자인으로 유명한 프랑스의"
    },
    {
        "brand_name": "Maison Kitsuné",
        "target_audience": "캐주얼하고 세련된 라이프스타일을 추구하는 사람들",
        "popular_products": [
            {
                "product_name": "폴스헤드 패치 레귤러 티셔츠",
                "category": "티셔츠",
                "season": "사계절",
                "price": 132525,
                "popularity_rank": 1,
                "tags": ["캐주얼", "모던", "데일리"],
                "description": "Maison Kitsuné의 시그니처 폭스 헤드 로고가 특징인 티셔츠입니다.",
                "gender": "male"
            },
            {
                "product_name": "캐주얼 팬츠",
                "category": "바지",
                "season": "사계절",
                "price": 463500,
                "popularity_rank": 2,
                "tags": ["캐주얼", "편안함", "사계절"],
                "description": "편안하면서도 스타일리시한 Maison Kitsuné의 캐주얼 팬츠입니다.",
                "gender": "male"
            },
            {
                "product_name": "베이비 폭스 패치 레귤러 가디건",
                "category": "가디건",
                "season": "사계절",
                "price": 483075,
                "popularity_rank": 1,
                "tags": ["캐주얼", "편안함", "사계절"],
                "description": "Maison Kitsuné의 시그니처 폭스 헤드 로고가 특징인 가디건입니다.",
                "gender":"female"
            },
            {
                "product_name": "베이비 폭스 패치 레귤러 조그 쇼츠",
                "category": "반바지",
                "season": "여름",
                "price": 283500,
                "popularity_rank": 2,
                "tags": ["캐주얼", "편안함", "여름"],
                "description": "편안하면서도 스타일리시한 Maison Kitsuné의 조그 쇼츠 팬츠입니다.",
                "gender":"female"
            }
        ],
        "website_url": "https://www.maisonkitsune.com",
        "description": "프랑스와 일본의 감성을 결합한 유니크한"
    }
]

# 데이터를 텍스트 리스트로 변환
data = []
for brand in brands_data:
    data.append(f"{brand['brand_name']} 브랜드는 {brand['description']}")
    for product in brand['popular_products']:
        data.append(f"{brand['brand_name']}의 인기 제품인 {product['product_name']}은(는) {product['description']} 가격은 {product['price']}원입니다.")
    data.append(f"{brand['brand_name']}의 웹사이트는 {brand['website_url']} 입니다.")

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

# 질문 분석 및 제품 또는 브랜드 추천 함수
def analyze_and_recommend_product_or_brand(question):
    seasons = ["봄", "여름", "가을", "겨울", "사계절"]
    categories = ["바지", "셔츠", "원피스", "자켓", "티셔츠", "가디건", "반바지", "레깅스", "치노", "데님"]

    # 브랜드 이름이 포함되어 있는지 확인
    selected_brand = None
    for brand in brands_data:
        if brand['brand_name'].lower() in question.lower():  # 소문자로 변환하여 대소문자 구분 없이 검색
            selected_brand = brand
            break
    
    for season in seasons:
        if season in question:
            for category in categories:
                if category in question:
                    season_category_products = []

                    # 특정 브랜드가 지정된 경우, 해당 브랜드 내에서 검색
                    if selected_brand:
                        season_category_products += [{**p, "brand_name": selected_brand["brand_name"]} for p in selected_brand['popular_products'] if season in p['season'] and category in p['category']]
                    else:
                        # 특정 브랜드가 지정되지 않은 경우, 모든 브랜드 내에서 검색
                        for brand in brands_data:
                            season_category_products += [{**p, "brand_name": brand["brand_name"]} for p in brand['popular_products'] if season in p['season'] and category in p['category']]

                    if season_category_products:
                        return season_category_products, "season_category_products"


  
    for brand in brands_data:
        # 브랜드에 대한 일반적인 질문 처리
        if f"{brand['brand_name']}" in question and "알려줘" in question:
            return brand, "brand_info"
        elif f"{brand['brand_name']}" in question and "인기 제품" in question:
            # 각 제품에 brand_name 추가
            products_with_brand = [{**product, "brand_name": brand["brand_name"]} for product in brand['popular_products']]
            return products_with_brand, "popular_products"
        elif f"{brand['brand_name']}" in question and "웹사이트" in question:
            return brand, "website"
        
        # 특정 제품에 대한 질문 처리
        for product in brand['popular_products']:
            if product['product_name'] in question:
                product_with_brand = {**product, "brand_name": brand["brand_name"]}
                return product_with_brand, "product_info"
        
        # 특정 조건 (시즌, 스타일, 성별 등)에 따른 추천 처리
        if "여름" in question and f"{brand['brand_name']}" in question:
            summer_products = [p for p in brand['popular_products'] if "여름" in p['season']]
            if summer_products:
                summer_products_with_brand = [{**p, "brand_name": brand["brand_name"]} for p in summer_products]
                return summer_products_with_brand, "season_products"
        if "사계절" in question and f"{brand['brand_name']}" in question:
            all_season_products = [p for p in brand['popular_products'] if "사계절" in p['season']]
            if all_season_products:
                all_season_products_with_brand = [{**p, "brand_name": brand["brand_name"]} for p in all_season_products]
                return all_season_products_with_brand, "season_products"
    
    # 30대 남성 타겟의 추천 처리
    if "30대 남성" in question:
        for brand in brands_data:
            if "30대" in brand["target_audience"]:
                return brand, "brand_info"

    # 특정 성별에 대한 추천 처리
    if "여성" in question:
        female_products = []
        for brand in brands_data:
            female_products += [{**p, "brand_name": brand["brand_name"]} for p in brand['popular_products'] if p['gender'] == "female"]
        if female_products:
            return female_products, "gender_products"
    
    if "남성" in question:
        male_products = []
        for brand in brands_data:
            male_products += [{**p, "brand_name": brand["brand_name"]} for p in brand['popular_products'] if p['gender'] == "male"]
        if male_products:
            return male_products, "gender_products"
    
    # 특정 스타일에 따른 추천 처리
    if "캐주얼" in question:
        casual_products = []
        for brand in brands_data:
            casual_products += [{**p, "brand_name": brand["brand_name"]} for p in brand['popular_products'] if "캐주얼" in p['tags']]
        if casual_products:
            return casual_products, "style_products"
    
    if "럭셔리" in question:
        luxury_products = []
        for brand in brands_data:
            luxury_products += [{**p, "brand_name": brand["brand_name"]} for p in brand['popular_products'] if "럭셔리" in p['tags']]
        if luxury_products:
            return luxury_products, "style_products"

    # 특정 조건에 맞는 브랜드 비교 처리
    if "저렴한" in question and "티셔츠" in question:
        comparison_result = []
        for brand in brands_data:
            comparison_result += [{**p, "brand_name": brand["brand_name"]} for p in brand['popular_products'] if "티셔츠" in p['category']]
        if comparison_result:
            cheapest_product = min(comparison_result, key=lambda x: x['price'])
            return cheapest_product, "product_info"

    # Fallback if no specific match
    return None, "unknown"


def create_natural_response(question, item, item_type):
    # 초기화: 기본 응답 메시지
    response = f"죄송합니다, 적절한 추천을 찾지 못했습니다. 😓"

    # 질문에 대한 응답 처리
    if not item:
        return response  # item이 없을 때 초기화된 기본 응답 반환

    if item_type == "brand_info":
        response = f"{item['brand_name']}은(는) {item['description']} 브랜드입니다. 자세한 정보는 {item['website_url']}에서 확인하세요. 🔍"
    elif item_type == "popular_products":
        # item이 리스트로 전달된 경우
        products_list = [{"brand": p['brand_name'], "name": p['product_name'], "description": p['description'], "price": p['price']} for p in random.sample(item, min(2, len(item)))]
        response = {
            "question": question,
            "products": products_list,
            "message": "더 많은 제품을 보시려면 추가 정보를 요청하세요. 😎"
        }
    elif item_type == "website":
        response = f"{item['brand_name']}의 공식 웹사이트는 {item['website_url']}입니다. 💻"
    elif item_type == "product_info":
        response = {
            "brand": item['brand_name'],
            "product_name": item['product_name'],
            "description": item['description'],
            "price": item['price']
        }
    elif item_type in ["season_products", "gender_products", "style_products", "season_category_products"]:
        products_list = [{"brand": p['brand_name'], "name": p['product_name'], "description": p['description'], "price": p['price']} for p in random.sample(item, min(2, len(item)))]
        response = {
            "question": question,
            "products": products_list,
            "message": "더 많은 제품을 보시려면 추가 정보를 요청하세요. 😎"
        }

    print(response)
    return response

# POST 엔드포인트 - 질문을 쿼리 매개변수로 수락
@router.post("/chatbot")
async def chatbot(question: str = Query(..., description="The question to ask the chatbot")):

    # 추천할 제품 또는 브랜드 결정
    recommended_item, item_type = analyze_and_recommend_product_or_brand(question)
    
    if recommended_item:
        natural_response = create_natural_response(question, recommended_item, item_type)
        return {"answer": natural_response}

    # 특정 항목을 찾지 못할 경우 유사성 기반 응답 제공
    result = query_huggingface_api(question, data)

    if isinstance(result, list):
        closest_index = np.argmax(result)
        response_text = data[closest_index]
        natural_response = create_natural_response(question, response_text, "unknown")
        return {"answer": natural_response}
    else:
        raise HTTPException(status_code=500, detail="Unexpected response format from API")
    
@router.get("/chatbot_hi")
async def chatbot_hi():
    return "안녕하세요, AZA의 챗봇 AZANG이에요. 👶 \n\n 다음과 같은 질문에 대한 답변을 드려요. 🪄 \n ex)'Adidas의 여름용 셔츠 추천해줘'"