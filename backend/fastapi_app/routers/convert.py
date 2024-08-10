from fastapi import APIRouter, HTTPException
import os
import torch
import smplx
import numpy as np
from convert.model import Camera, process_image, get_camera_matrices, triangulate_points, augment_data, adjust_loss_weights_for_bmi, smplify, calculate_body_measurements, calculate_circumference, calculate_final_measurements
from .upload import uploaded_file_paths
from .user_data import user_data_store

router = APIRouter()

recent_measurements = {}

@router.post("/predict")
async def predict():
    print("Uploaded file paths:", uploaded_file_paths)
    if len(uploaded_file_paths) < 3:
        raise HTTPException(status_code=400, detail="Not enough files uploaded")

    try:
        camera = Camera()

        # Mediapipe를 사용해 2D 키포인트 추출
        keypoints_2d_list = []
        for file_path in uploaded_file_paths[:3]:  # 업로드된 첫 3개의 파일 사용
            keypoints_2d = process_image(file_path)
            if keypoints_2d is None:
                raise HTTPException(status_code=400, detail="Unable to extract keypoints from the image.")
            keypoints_2d_list.append(keypoints_2d)
        print("2D keypoints extracted:", keypoints_2d_list)

        # 3개의 이미지에 대해 카메라 행렬 및 3D 키포인트 추정
        camera_matrices = get_camera_matrices()[:3]
        keypoints_3d = triangulate_points(keypoints_2d_list, camera_matrices)
        print("3D keypoints reconstructed:", keypoints_3d)
        
        # 데이터 증폭
        augmented_keypoints_3d = augment_data([keypoints_3d])
        
        # BMI 계산
        height_cm = user_data_store["height"]
        weight_kg = user_data_store["weight"]
        gender = user_data_store["gender"]
        bmi = weight_kg / (height_cm / 100) ** 2
        weights = adjust_loss_weights_for_bmi(bmi)
        
        # SMPL 모델 경로 
        if(gender == "female"):
            smpl_model_path = "/Users/heejin/Downloads/Backend/backend/fastapi_app/model/smplx/SMPLX_FEMALE.pkl"
            print("Loading SMPL model from:", smpl_model_path)
            smpl_model = smplx.create(smpl_model_path, model_type='smplx', gender='female', ext='pkl')
        elif(gender == "male"):
            smpl_model_path = "/Users/heejin/Downloads/Backend/backend/fastapi_app/model/smplx/SMPLX_MALE.pkl"
            print("Loading SMPL model from:", smpl_model_path)
            smpl_model = smplx.create(smpl_model_path, model_type='smplx', gender='male', ext='pkl')
        
        # 초기 파라미터 설정
        initial_params = {
            'betas': torch.randn((1, 10)),  # 무작위 초기화 대신 정규분포 초기화
            'body_pose': torch.zeros((1, smpl_model.NUM_BODY_JOINTS * 3)),
            'global_orient': torch.zeros((1, 3)),
            'transl': torch.zeros((1, 3))
        }
        print("Performing SMPL optimization...")

        # 최적화 수행
        optimized_params = smplify(np.concatenate(augmented_keypoints_3d), smpl_model, camera, initial_params, weights)
        print("Optimization complete:", optimized_params)


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
            'id': [os.path.basename(file_path) for file_path in uploaded_file_paths],
            'sex': 'female',
            'chest_circumference': calculate_circumference(vertices, chest_indices),
            'waist_circumference': calculate_circumference(vertices, waist_indices),
            'thigh_circumference': calculate_circumference(vertices, thigh_indices),
            'hip_circumference': calculate_circumference(vertices, hip_indices),
            'neck_circumference': calculate_circumference(vertices, neck_indices)
        })

         # 최근 measurements를 메모리에 저장
        recent_measurements["last"] = calculate_final_measurements(measurements)

        # 예측 결과를 반환
        return {"measurements": measurements}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model execution failed: {str(e)}")

    finally:
        # 입력 파일을 삭제
        for file_path in uploaded_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

@router.get("/measurements")
async def get_measurements():
    if "last" not in recent_measurements:
        raise HTTPException(status_code=404, detail="No measurements available. Please run a prediction first.")
    
    return recent_measurements["last"]