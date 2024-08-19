from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.fastapi_app.model.ml_prediction import predict_clothing_size

# APIRouter 인스턴스 생성
router = APIRouter()

# 최종 예측 결과를 저장할 변수
predicted_clothing_size = None

# 예측을 위한 POST 엔드포인트 정의
@router.post("/predict-clothing-size/")
async def predict_clothing_size_endpoint():
    try:
        global predicted_clothing_size  # 전역 변수로 설정
        
        # 하드코딩된 입력값 설정
        gender = "female"
        category = "반팔"
        brand = "아디다스"
        
        if category == "바지":
            height = 170.0
            weight = 65.0
            bmi = 22.5
            bmi_class = "normal"
            chest_length = 85.0
            inseam = 80.0
            outseam = 100.0
            arm_length = 60.0
            shoulder_distance = 40.0
            
            result = predict_clothing_size(
                gender, category, brand, height=height, weight=weight, bmi=bmi, bmi_class=bmi_class, 
                chest_length=chest_length, inseam=inseam, outseam=outseam, arm_length=arm_length, 
                shoulder_distance=shoulder_distance
            )
        elif category == "긴팔" or category == "반팔":
            height = 165.0
            weight = 60.0
            bmi_class = "overweight"
            waist_length = 75.0
            hip = 90.0
            inseam = 80.0
            outseam = 105.0
            arm_length = 62.0
            
            result = predict_clothing_size(
                gender, category, brand, height=height, weight=weight, bmi_class=bmi_class, 
                waist_length=waist_length, hip=hip, inseam=inseam, outseam=outseam, arm_length=arm_length
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid category")

        predicted_clothing_size = result["predicted_clothing_size"]
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# GET 요청을 처리하는 엔드포인트 추가
@router.get("/get-predicted-clothing-size/")
async def get_predicted_clothing_size():
    if predicted_clothing_size is None:
        raise HTTPException(status_code=404, detail="No prediction available. Please run a prediction first.")
    
    return {"predicted_clothing_size": predicted_clothing_size}
