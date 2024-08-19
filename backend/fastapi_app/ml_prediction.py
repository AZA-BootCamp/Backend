from sklearn.ensemble import RandomForestClassifier
import os
import numpy as np
import joblib
from fastapi import HTTPException
from backend.fastapi_app.model.train_model import CustomSVMClassifier

class MLModelPredictor:
    def __init__(self, gender: str, category: str, brand: str):
        self.model_name = self.get_model_name(gender, category, brand)
        if self.model_name is None:
            raise HTTPException(status_code=400, detail="No valid model name found.")
        self.model_path = self.get_model_path(self.model_name)
        self.model = self.load_model()

    def get_model_name(self, gender: str, category: str, brand: str) -> str:
        if gender == 'female' and category == '바지':
            if brand == '아디다스':
                return 'women_pants_adidas_model.pkl'
            elif brand == '캘빈클라인':
                return 'women_pants_cv_model.pkl'
            elif brand == '나이키':
                return 'women_pants_nike_model.pkl'
            elif brand == 'Tommy hilfiger':
                return 'women_pants_tommy_model.pkl'
        elif gender == 'female' and category == '긴팔':
            if brand == '아디다스':
                return 'woman_long_shirt_adidas_model.pkl'
            elif brand == '캘빈클라인':
                return 'woman_long_shirt_ck_model.pkl'
            elif brand == 'kenzo':
                return 'woman_long_shirt_kenzo_model.pkl'
            elif brand == '메종키츠네':
                return 'woman_long_shirt_mk_model.pkl'
            elif brand == '나이키':
                return 'woman_long_shirt_nike_model.pkl'
            elif brand == '폴로랄프로렌':
                return 'woman_long_shirt_polo_model.pkl'
            elif brand == 'saint laurent':
                return 'woman_long_shirt_sl_model.pkl'
            elif brand == 'Tommy hilfiger':
                return 'woman_long_shirt_tommy_model.pkl'
        elif gender == 'female' and category == '반팔':
            if brand == '아디다스':
                return 'test.pkl'  # 변경된 모델명으로 설정
        elif gender == 'male' and category == '바지':
            if brand == '폴로랄프로렌':
                return 'man_pants_polo_model.pkl'
            elif brand == '아디다스':
                return 'men_pants_adidas_model.pkl'
            elif brand == 'kenzo':
                return 'men_pants_kenzo_model.pkl'
            elif brand == '나이키':
                return 'men_pants_nike_model.pkl'
            elif brand == 'Tommy hilfiger':
                return 'men_pants_tommy_model.pkl'
        elif gender == 'male' and category == '긴팔':
            if brand == '아디다스':
                return 'man_long_shirt_adidas_model.pkl'
            elif brand == '캘빈클라인':
                return 'man_long_shirt_ck_model.pkl'
            elif brand == 'kenzo':
                return 'man_long_shirt_kenzo_model.pkl'
            elif brand == '메종키츠네':
                return 'man_long_shirt_mk_model.pkl'
            elif brand == '나이키':
                return 'man_long_shirt_nike_model.pkl'
            elif brand == '폴로랄프로렌':
                return 'man_long_shirt_polo_model.pkl'
            elif brand == 'saint laurent':
                return 'man_long_shirt_sl_model.pkl'
            elif brand == 'Tommy hilfiger':
                return 'man_long_shirt_tommy_model.pkl'
        elif gender == 'male' and category == '반팔':
            if brand == '아디다스':
                return 'man_short_shirt_adidas_model.pkl'
            elif brand == '캘빈클라인':
                return 'man_short_shirt_ck_model.pkl'
            elif brand == 'kenzo':
                return 'man_short_shirt_kenzo_model.pkl'
            elif brand == '메종키츠네':
                return 'man_short_shirt_mk_model.pkl'
            elif brand == '나이키':
                return 'man_short_shirt_nike_model.pkl'
            elif brand == '폴로랄프로렌':
                return 'man_short_shirt_polo_model.pkl'
            elif brand == 'saint laurent':
                return 'man_short_shirt_sl_model.pkl'
            elif brand == 'Tommy hilfiger':
                return 'man_short_shirt_tommy_model.pkl'
        else:
            return None  # 모델 이름을 찾지 못하면 None을 반환

    def get_model_path(self, model_name: str) -> str:
        base_path = '/Users/minkyukang/KSeb Project(Backend)/Backend/backend/fastapi_app/model/ml_prediction'
        model_path = os.path.join(base_path, model_name)
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found at {model_path}")
        return model_path

    def load_model(self):
        try:
            model = joblib.load(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")
            return model
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model from {self.model_path}: {str(e)}")

    def predict(self, input_data):
        try:
            prediction = self.model.predict(input_data)
            return prediction
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")


def predict_clothing_size(gender, category, brand, **kwargs):
    predictor = MLModelPredictor(gender, category, brand)

    if category == '바지':
        input_data = [[
            kwargs['height'], kwargs['weight'], kwargs['bmi'], kwargs['bmi_class'], 
            kwargs['chest_length'], kwargs['inseam'], kwargs['outseam'], kwargs['arm_length'], 
            kwargs['shoulder_distance']
        ]]
    elif category == '긴팔' or category == '반팔':
        input_data = [[
            kwargs['height'], kwargs['weight'], kwargs['bmi_class'], kwargs['waist_length'], 
            kwargs['hip'], kwargs['inseam'], kwargs['outseam'], kwargs['arm_length']
        ]]
    else:
        raise HTTPException(status_code=400, detail="Invalid category")

    predicted_size = predictor.predict(input_data)
    
    return {"predicted_clothing_size": predicted_size[0]}
