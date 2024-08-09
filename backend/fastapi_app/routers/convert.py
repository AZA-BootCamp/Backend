from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import os
from convert.model import Camera, process_image, get_camera_matrices, triangulate_points, augment_data, adjust_loss_weights_for_bmi, smplify, calculate_body_measurements, calculate_circumference
import torch
import smplx
import numpy as np

router = APIRouter()

# 메모리에 measurements를 저장할 변수
recent_measurements = {}

@router.post("/predict")
async def predict(
    file1: UploadFile = File(...), 
    file2: UploadFile = File(...), 
    file3: UploadFile = File(...), 
    height_cm: float = Form(...), 
    weight_kg: float = Form(...)
):
    try:
        # 저장할 디렉토리와 파일 이름 설정
        input_dir = "backend/fastapi_app/uploaded_files_test"
        os.makedirs(input_dir, exist_ok=True)
        
        files = [file1, file2, file3]
        input_paths = []
        
        for i, file in enumerate(files):
            input_path = os.path.join(input_dir, f"{i}_{file.filename}")
            input_paths.append(input_path)
            with open(input_path, "wb") as f:
                f.write(await file.read())

        camera = Camera()

        # Mediapipe를 사용해 2D 키포인트 추출
        keypoints_2d_list = []
        for input_path in input_paths:
            keypoints_2d = process_image(input_path)
            if keypoints_2d is None:
                raise HTTPException(status_code=400, detail="Unable to extract keypoints from the image.")
            keypoints_2d_list.append(keypoints_2d)

        # 3개의 이미지에 대해 카메라 행렬 및 3D 키포인트 추정
        camera_matrices = get_camera_matrices()[:3]  # 예시로 3개의 카메라 행렬만 사용
        keypoints_3d = triangulate_points(keypoints_2d_list, camera_matrices)
        
        # 데이터 증폭
        augmented_keypoints_3d = augment_data([keypoints_3d])
        
        # BMI 계산
        bmi = weight_kg / (height_cm / 100) ** 2
        weights = adjust_loss_weights_for_bmi(bmi)
        
        # SMPL 모델 경로 (예시로 여성 모델을 사용)
        smpl_model_path = "/Users/heejin/Downloads/Backend/backend/fastapi_app/model/SMPLX_FEMALE.pkl"
        smpl_model = smplx.create(smpl_model_path, model_type='smplx', gender='female', ext='pkl')
        
        # 초기 파라미터 설정
        initial_params = {
            'betas': torch.zeros((1, 10)),
            'body_pose': torch.zeros((1, smpl_model.NUM_BODY_JOINTS * 3)),
            'global_orient': torch.zeros((1, 3)),
            'transl': torch.zeros((1, 3))
        }

        # 최적화 수행
        optimized_params = smplify(np.concatenate(augmented_keypoints_3d), smpl_model, camera, initial_params, weights)
        
        # 최적화된 파라미터를 사용하여 최종 3D 모델 생성
        smpl_output = smpl_model(
            betas=torch.tensor(optimized_params['betas'], dtype=torch.float32),
            body_pose=torch.tensor(optimized_params['body_pose'], dtype=torch.float32),
            global_orient=torch.tensor(optimized_params['global_orient'], dtype=torch.float32),
            transl=torch.tensor(optimized_params['transl'], dtype=torch.float32)
        )
        
        vertices = smpl_output.vertices.detach().cpu().numpy().squeeze()

        # 신체 치수 계산
        measurements = calculate_body_measurements(vertices, height_cm, weight_kg, bmi)
        
        waist_indices = [3231, 3274, 6115, 3352, 6801, 5992]
        chest_indices = [4416, 6025, 5569, 8307, 3261, 6307]
        thigh_indices = [3603, 3541]
        hip_indices = [5949, 3959, 3866, 5685, 8407, 6832, 6617]
        neck_indices = [3213, 3199, 1326, 6213, 5973]

        measurements.update({
            'id': [file.filename for file in files],
            'sex': 'female',
            'chest_circumference': calculate_circumference(vertices, chest_indices),
            'waist_circumference': calculate_circumference(vertices, waist_indices),
            'thigh_circumference': calculate_circumference(vertices, thigh_indices),
            'hip_circumference': calculate_circumference(vertices, hip_indices),
            'neck_circumference': calculate_circumference(vertices, neck_indices)
        })

        # 최근 measurements를 메모리에 저장
        recent_measurements["last"] = measurements

        # 예측 결과를 반환합니다.
        return {
            "measurements": measurements,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model execution failed: {str(e)}")

    finally:
        # 입력 파일을 삭제합니다.
        for input_path in input_paths:
            if os.path.exists(input_path):
                os.remove(input_path)

@router.get("/measurements")
async def get_measurements():
    if "last" not in recent_measurements:
        raise HTTPException(status_code=404, detail="No measurements available. Please run a prediction first.")
    
    return recent_measurements["last"]
