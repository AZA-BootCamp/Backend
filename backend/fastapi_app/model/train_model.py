# -*- coding: utf-8 -*-
# seed 고정(같은 코드를 돌려도 같은 결과가 나오게 함)
import random
import os
import numpy as np

def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)

seed_everything(42)

# 경고 메시지 무시
import warnings

warnings.filterwarnings('ignore')

# 필요한 라이브러리
import pandas as pd
import math
import json
import os

import pandas as pd

df_actors = pd.read_csv('/Users/minkyukang/KSeb Project(Backend)/Backend/backend/fastapi_app/model/df_actors.csv')

# 어깨 길이에 평균 절대 오차(MAE) 반영
# 모델링과 좌표값을 바탕으로 출력한 값에 오류가 있음을 인정 => mae 반영
import pandas as pd

# 각 신체부위에 대한 MAE(평균절대오차)
mae_values = {
    #'arm length': 2.387972010552343,
    #'inseam': 3.6551313702016466,
    #'outseam': 4.704287962982934,
    #'chest length': 4.171392550752021,
    #'waist length': 3.320629568414946,
    #'hip': 3.540643063580719,
    'shoulder_distance': 1.8707145790016395
}

# 각 칼럼에 대해 MAE의 절반 값을 더하기
for column in mae_values:
    half_mae = mae_values[column] / 2
    df_actors[column] = df_actors[column] + half_mae

# 성별에 따른 데이터 분류
df_actors_female = df_actors[df_actors['sex'] == 'female']

# 머신러닝 모델 학습을 위한 데이터 증강(여성)
import pandas as pd
import numpy as np
from sklearn.utils import resample

# 1. 노이즈 추가 방법 적용 - 기존 데이터에 작은 변동을 더하여 데이터의 다양성 높이기
def add_noise(df, noise_level, n_samples):
    n_samples_to_add = n_samples - len(df)
    augmented_data = []

    # 숫자 열만 선택
    numeric_columns = df.select_dtypes(include=[np.number]).columns

    for _ in range(n_samples_to_add):
        noisy_df = df.sample(n=1, replace=True).copy()
        for column in numeric_columns:
            noise = np.random.normal(0, noise_level, noisy_df[column].shape)
            noisy_df[column] += noise * noisy_df[column]
        augmented_data.append(noisy_df)

    return pd.concat([df] + augmented_data, ignore_index=True)

# 노이즈 추가하여 데이터 증강
noise_total_samples = 10000  # 생성할 총 데이터 샘플 수

df_actors_female = add_noise(df_actors_female, noise_level=0.025, n_samples=noise_total_samples) # noise_level = 0.01: 원본 데이터 값의 1% 크기의 변동이 추가

# 2. 스케일 변환 방법 적용 - 데이터의 스케일을 약간 변경하여 데이터의 다양성 증가
def scale_data(dataframe, scale_range=(0.95, 1.05), n_samples=10):
    n_samples_to_add = n_samples - len(dataframe)
    augmented_data = []
    for _ in range(n_samples_to_add):
        scaled_df = dataframe.sample(n=1, replace=True).copy()
        for column in scaled_df.columns:
            scale_factor = np.random.uniform(scale_range[0], scale_range[1], scaled_df[column].shape)
            scaled_df[column] *= scale_factor
        augmented_data.append(scaled_df)
    return pd.concat([dataframe] + augmented_data, ignore_index=True)

# 스케일 변환하여 데이터 증강
scale_total_samples = 10000  # 생성할 총 데이터 샘플 수

df_actors_female = scale_data(df_actors_female, scale_range=(0.95, 1.05), n_samples=scale_total_samples) # 원본 데이터 값이 100인 경우: 스케일링 팩터가 0.97~1.03 -> 변환된 새로운 값은 97~103

print("\nNumber of samples in resampled dataframe:", len(df_actors_female))

# BMI 지수 및 BMI 클래스 재부여
import pandas as pd

# BMI 계산 함수
def calculate_bmi(height, weight):
    height_m = height / 100  # 키를 미터로 변환
    bmi = weight / (height_m ** 2)
    return bmi

# BMI에 따른 클래스 할당 함수
def bmi_to_class(bmi):
    if bmi < 18.5:
        return 'underweight'
    elif 18.5 <= bmi < 24.9:
        return 'normal'
    elif 25 <= bmi < 29.9:
        return 'overweight'
    elif 30 <= bmi < 34.9:
        return 'obese'
    else:
        return 'extremely obese'

# BMI 계산 및 클래스 할당
df_actors_female['BMI'] = df_actors_female.apply(lambda row: calculate_bmi(row['height'], row['weight']), axis=1)
df_actors_female['BMI Class'] = df_actors_female['BMI'].apply(bmi_to_class)

"""###여성반팔"""
# 쇼핑몰 데이터 불러오기(여성 반팔 사이즈 기준표)
import pandas as pd

women_short_shirt = pd.read_excel("/Users/minkyukang/KSeb Project(Backend)/Backend/backend/fastapi_app/model/musinsa women short shirt.xlsx")

"""##폴로랄프로렌"""
# 필요한 열 인덱스를 리스트로 명시
selected_columns = [0] + list(range(2, 6))

women_short_shirt_polo = women_short_shirt.iloc[:, selected_columns]

# 첫 번째 열을 제외한 나머지 열의 첫 번째 행을 새로운 칼럼명으로 설정
new_columns = women_short_shirt_polo.iloc[0, 1:].values
women_short_shirt_polo.columns = ['여성 반팔'] + list(new_columns)

# 첫 번째 행을 인덱스로 설정
women_short_shirt_polo = women_short_shirt_polo[1:]

# 인덱스를 리셋하여 인덱스 컬럼 제거
women_short_shirt_polo = women_short_shirt_polo.reset_index(drop=True)

# '여성 반팔' 열을 인덱스로 설정
women_short_shirt_polo = women_short_shirt_polo.set_index('여성 반팔')

# 결측값인 행 모두 삭제
women_short_shirt_polo = women_short_shirt_polo.dropna()

# 모든 칼럼 데이터 유형을 수치형(float)으로 변환
women_short_shirt_polo = women_short_shirt_polo.astype(float)

# <필요시> women_short_shirt_polo 데이터프레임 전치행렬 변경
women_short_shirt_polo = women_short_shirt_polo.T

# json 신체 데이터 불러오기
# 새로운 가슴 둘레 칼럼 추가(chest length / 2)
df_actors_female['chest length_half'] = df_actors_female['chest length'] / 2

# 'women_short_shirt_polo' 칼럼 추가
df_actors_female['women_short_shirt_polo'] = 0  # 열 초기화

"""###사이즈표 전처리(유클리드 거리 적용)
-> women_short_shirt_polo 데이터프레임에서 'chest length'와 '어깨' 칼럼을 하나의 좌표 상의 점으로 설정 -> df_actors 데이터프레임에서 'shoulder_distance'와 'chest length_half' 칼럼을 하나의 좌표 상의 점으로 설정

x좌표: 어깨 길이 (shoulder_distance, 어깨)
y좌표: 가슴 둘레 (chest length_half, Chest)

-> 가까운 점이 가진 women_short_shirt_polo 데이터프레임의 '남성 반팔' 인덱스 칼럼 값을 df_actors 데이터프레임의 'POLO_반팔' 칼럼에 대입
"""

##좌표로 찾기
import pandas as pd
import numpy as np
from scipy.spatial import distance

# 데이터프레임 복사
df_actors_female_size1 = df_actors_female.copy()

# 사이즈 순서 정의
size_order = ['S', 'M', 'L', 'XL']

# 빈 리스트 생성
sizes = []

# 가장 가까운 좌표 찾기
for _, actor in df_actors_female_size1.iterrows():
    min_distance = float('inf')
    closest_size = None
    actor_point = (actor['shoulder_distance'], actor['chest length_half'])

    for size in size_order:
        size_point = (women_short_shirt_polo.loc[size, '어깨'], women_short_shirt_polo.loc[size, 'chest length'])
        dist = distance.euclidean(actor_point, size_point)
        if dist < min_distance:
            min_distance = dist
            closest_size = size

    sizes.append(closest_size)

# 결과를 원래 데이터프레임에 추가
df_actors_female_size1.loc[df_actors_female_size1['sex'] == 'female', 'women_short_shirt_polo'] = sizes

# 정수 인코딩 - 모델 학습을 위해서는 문자열 데이터를 정수 형태로 변환해줘야 함
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# LabelEncoder 객체 생성
label_encoder = LabelEncoder()

# 'women_short_shirt_polo' 열을 정수 인코딩
df_actors_female_size1['BMI Class'] = label_encoder.fit_transform(df_actors_female_size1['BMI Class'])
df_actors_female_size1['women_short_shirt_polo'] = label_encoder.fit_transform(df_actors_female_size1['women_short_shirt_polo'])

# Min-Max 스케일링
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# 스케일링 필요한 칼럼 선택(연속형 변수)
scaling_columns = ['height',	'weight',	'BMI', 'chest length',	'waist length',	'hip',	'inseam',
                    'outseam',	'arm length']

# Min-Max Scaler 객체 생성
scaler = MinMaxScaler()

# 선택한 칼럼에 대해 Min-Max Scaler 적용
df_actors_female_size1[scaling_columns] = scaler.fit_transform(df_actors_female_size1[scaling_columns])

# 독립변수와 종속변수 설정
X = df_actors_female_size1[['height', 'weight', 'BMI Class', 'waist length', 'hip', 'inseam', 'outseam', 'arm length']]
y = df_actors_female_size1['women_short_shirt_polo']

# 훈련 데이터와 테스트 데이터로 분리 (오버샘플링 적용)
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from collections import Counter

# SMOTE 객체 생성
smote = SMOTE(random_state=42)

# 8:2 비율로 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 오버샘플링 적용
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

"""###분류 모델 앙상블 및 그리드서치 활용
"""
"""####SVM"""

from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

model_svm = SVC(decision_function_shape='ovo', probability=True)  # ovo: one-vs-one strategy for multi-class classification
                                                                  # probability=True: 확률 예측 활성화
model_svm_hyper_parmas = {
                          'C': [0.1, 1, 10, 100], # 모델 학습 규제 정도 조정
                          'gamma': [1, 0.1, 0.01, 0.001], # 감마값 지정
                          'kernel': ['linear', 'rbf'] # svm에서 사용할 사용할 커널 유형 지정
                         }

model4 = GridSearchCV(model_svm, param_grid=model_svm_hyper_parmas, cv=5, scoring = 'accuracy', refit=True, return_train_score=True, n_jobs = -1)
model4.fit(X_train, y_train)

print(f'최상의 하이퍼 파라미터: {model4.best_params_}')
print(f'최상의 하이퍼 파라미터일 때 정확도: {model4.best_score_}')

# 과소적합, 과대적합 가능성 확인
print(model4.score(X_train, y_train))
print(model4.score(X_test, y_test))

# 모델 성능 검증
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

estimator_svm = model4.best_estimator_
pred_estimator_svm = estimator_svm.predict(X_test)

print(classification_report(y_test, pred_estimator_svm))
print(accuracy_score(y_test, pred_estimator_svm))

"""### 최적의 모델 저장

최종 모델 저장
-> 모델 옷 사이즈 후기 가중치 반영을 위해,

위에서 가장 성능이 좋은 모델 선택
아래에서 가중치가 반영된 클래스 제작 및 모델로 재학습
예시) 만약에 위에서 svm이 가장 좋은 성능 모델로 나왔다면, 아래에서 가중치를 반영한 커스텀 SVM 클래스 제작 및 모델 재학습

더 크거나 작은 사이즈를 추천하는 확률에 당첨됐을 때는 일단 한 칸 위 또는 아래로 옷 사이즈 클래스 추천
"""

from sklearn.svm import SVC
from sklearn.base import BaseEstimator, ClassifierMixin

# 커스텀 CustomSVMClassifier 정의
class CustomSVMClassifier(BaseEstimator, ClassifierMixin):
    # 클래스 불러오기 위해 모델의 모든 하이퍼파라미터 정의
    def __init__(self,
                 C=1.0,
                 kernel='rbf',
                 degree=3,
                 gamma='scale',
                 coef0=0.0,
                 shrinking=True,
                 probability=False,
                 tol=1e-3,
                 cache_size=200,
                 class_weight=None,
                 verbose=False,
                 max_iter=-1,
                 decision_function_shape='ovr',
                 break_ties=False,
                 random_state=None,
                 label_encoder=None):

        self.C = C # Expose C as an attribute
        self.kernel = kernel # Expose kernel as an attribute
        self.degree = degree
        self.gamma = gamma
        self.coef0 = coef0
        self.shrinking = shrinking
        self.probability = probability
        self.tol = tol
        self.cache_size = cache_size
        self.class_weight = class_weight
        self.verbose = verbose
        self.max_iter = max_iter
        self.decision_function_shape = decision_function_shape
        self.break_ties = break_ties
        self.random_state = random_state

        self.svc = SVC(C=self.C, # Use self.C to refer to the attribute
                       kernel=self.kernel, # Use self.kernel to refer to the attribute
                       degree=degree,
                       gamma=gamma,
                       coef0=coef0,
                       shrinking=shrinking,
                       probability=probability,
                       tol=tol,
                       cache_size=cache_size,
                       class_weight=class_weight,
                       verbose=verbose,
                       max_iter=max_iter,
                       decision_function_shape=decision_function_shape,
                       break_ties=break_ties,
                       random_state=random_state)

        self.label_encoder = label_encoder

    def adjust_size(self, predicted_size):
            sizes = label_encoder.classes_
            size_index = np.where(sizes == predicted_size)[0][0]

            # 3%는 더 작은 사이즈, 95%는 같은 사이즈, 2%는 더 큰 사이즈 추천
            adjustment_probabilities = [0.03, 0.95, 0.02]
            adjustment = np.random.choice([-1, 0, 1], p=adjustment_probabilities)

            adjusted_index = size_index + adjustment

            # 인덱스 범위 조정 (예: XS에서 더 작은 사이즈는 없음, XXL에서 더 큰 사이즈는 없음)
            if adjusted_index < 0:
                adjusted_index = 0
            elif adjusted_index >= len(sizes):
                adjusted_index = len(sizes) - 1

            # 최종 사이즈 반환
            return sizes[adjusted_index]

    def fit(self, X, y):
        self.svc.fit(X, y)
        return self

    def predict(self, X):
        raw_predictions = self.svc.predict(X)
        adjusted_predictions = [self.adjust_size(self.label_encoder.inverse_transform([pred])[0]) for pred in raw_predictions]
        return self.label_encoder.transform(adjusted_predictions)

# 기존 모델이 그리드서치 및 하이퍼파라미터를 설정하지 않아도 될 정도 => 그냥 단순히 모델 학습시키기
remodel_svm = CustomSVMClassifier(decision_function_shape='ovo', probability=True, label_encoder=label_encoder)
remodel_svm.fit(X_train, y_train)

# 과소적합, 과대적합 가능성 확인
print(remodel_svm.score(X_train, y_train))
print(remodel_svm.score(X_test, y_test))

# 모델 성능 검증
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

re_pred_estimator_svm = remodel_svm.predict(X_test)

print(classification_report(y_test, re_pred_estimator_svm))
print(accuracy_score(y_test, re_pred_estimator_svm))

# 최종 저장할 모델
import joblib

woman_short_shirt_polo_model = remodel_svm

# 모델 저장
joblib.dump(woman_short_shirt_polo_model, '/Users/minkyukang/KSeb Project(Backend)/Backend/backend/fastapi_app/model/ml_prediction/test.pkl') # 확장자 .pkl