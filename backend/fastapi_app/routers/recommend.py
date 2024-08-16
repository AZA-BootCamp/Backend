from fastapi import APIRouter, HTTPException
from ml_prediction import predict_clothing_size

# APIRouter 인스턴스 생성
router = APIRouter()

# 예측을 위한 POST 엔드포인트 정의 (하드코딩된 값 사용)
@router.post("/predict-clothing-size/")
async def predict_clothing_size_endpoint(
    gender: str, 
    category: str, 
    brand: str
):
    try:
        # 하드코딩된 입력값 설정
        if category == "바지":
            height = 170.0
            weight = 65.0
            bmi = 22.5
            bmi_class = "normal"  # BMI 클래스에 문자열 값 사용
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
            bmi_class = "overweight"  # BMI 클래스에 문자열 값 사용
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

        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# GET 요청을 처리하는 엔드포인트 추가
@router.get("/predict-clothing-size/")
async def get_clothing_size_example():
    # 예시로 고정된 데이터를 반환
    example_data = {
        "message": "ML recommendation COMMUNICATION COMPLETE"
    }
    return example_data

# 직접 실행을 위한 코드 추가
if __name__ == "__main__":
    # 하드코딩된 예시 값
    gender = "female"
    category = "반팔"
    brand = "아디다스"
    
    # 예측 결과 확인
    result = predict_clothing_size_endpoint(gender, category, brand)
    print(result)
