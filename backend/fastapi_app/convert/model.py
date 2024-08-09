import cv2
import numpy as np
import mediapipe as mp
import torch
from scipy.optimize import minimize
import os
 
num_betas = 10

# Mediapipe Pose 모델 설정
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# 카메라 클래스
class Camera:
    def __init__(self, focal_length=1000, img_center=(512, 512)):
        self.focal_length = focal_length
        self.img_center = img_center

    def project(self, points):
        projected = points[:, :2] / points[:, 2, np.newaxis] * self.focal_length + self.img_center
        return projected

# 이미지 처리 함수
def process_image(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        keypoints_2d = np.array([[landmark.x * image.shape[1], landmark.y * image.shape[0]] for landmark in landmarks])
        return keypoints_2d
    else:
        return None

# 카메라 행렬 예제 (내부 매개변수 및 외부 매개변수 포함)
def get_camera_matrices():
    intrinsic_matrix = np.array([
        [800, 0, 320],
        [0, 800, 240],
        [0, 0, 1]
    ])
    rotation_matrix_1 = np.eye(3)
    translation_vector_1 = np.array([0, 0, 0])
    rotation_matrix_2 = np.eye(3)
    translation_vector_2 = np.array([0.1, 0, 0])
    extrinsic_matrix_1 = np.hstack((rotation_matrix_1, translation_vector_1.reshape(3, 1)))
    extrinsic_matrix_2 = np.hstack((rotation_matrix_2, translation_vector_2.reshape(3, 1)))
    camera_matrix_1 = intrinsic_matrix @ extrinsic_matrix_1
    camera_matrix_2 = intrinsic_matrix @ extrinsic_matrix_2
    return [camera_matrix_1, camera_matrix_2]

# 2D 키포인트를 사용하여 3D 키포인트 추정
def triangulate_points(keypoints_2d_list, camera_matrices):
    keypoints_2d = np.array(keypoints_2d_list)
    points_4d_hom = cv2.triangulatePoints(camera_matrices[0], camera_matrices[1], keypoints_2d[0].T, keypoints_2d[1].T)
    points_4d = points_4d_hom / points_4d_hom[3]
    return points_4d[:3].T

# 데이터 증폭 함수
def augment_data(keypoints_3d_list):
    augmented_data = []
    for keypoints in keypoints_3d_list:
        augmented_data.append(keypoints)
        noise = np.random.normal(0, 0.02, keypoints.shape)
        augmented_data.append(keypoints + noise)
        if len(keypoints_3d_list) > 1:
            other_keypoints = keypoints_3d_list[np.random.randint(0, len(keypoints_3d_list))]
            crossover = np.vstack((keypoints[:len(keypoints)//2], other_keypoints[len(keypoints)//2:]))
            augmented_data.append(crossover)
        rotation_matrix = np.array([[np.cos(np.pi/6), -np.sin(np.pi/6)], [np.sin(np.pi/6), np.cos(np.pi/6)]])
        rotated_keypoints = keypoints[:, :2] @ rotation_matrix.T
        augmented_data.append(np.hstack((rotated_keypoints, keypoints[:, 2:])))
        translation = np.random.uniform(-0.1, 0.1, size=keypoints.shape)
        augmented_data.append(keypoints + translation)
        scale_factor = np.random.uniform(0.9, 1.1)
        augmented_data.append(keypoints * scale_factor)
    return augmented_data

# BMI에 따른 손실 가중치 조정 함수
def adjust_loss_weights_for_bmi(bmi):
    if bmi < 18.5:
        weights = {'keypoint_loss': 1.0, 'pelvis_loss': 0.2, 'shoulder_loss': 0.2, 'leg_symmetry_loss': 0.2, 'scale_loss': 1.5}
    elif 18.5 <= bmi < 25:
        weights = {'keypoint_loss': 1.0, 'pelvis_loss': 0.1, 'shoulder_loss': 0.1, 'leg_symmetry_loss': 0.1, 'scale_loss': 1.0,
                   'arm_length_loss': 10.0, 'inseam_loss': 0.8, 'outseam_loss': 0.8, 'waist_loss': 0.8, 'chest_loss': 1.2, 'hip_loss': 1.2}
    elif 25 <= bmi < 30:
        weights = {'keypoint_loss': 1.0, 'pelvis_loss': 0.1, 'shoulder_loss': 0.1, 'leg_symmetry_loss': 0.1, 'scale_loss': 0.8}
    elif 30 <= bmi < 35:
        weights = {'keypoint_loss': 1.0, 'pelvis_loss': 0.1, 'shoulder_loss': 0.1, 'leg_symmetry_loss': 0.1, 'scale_loss': 0.5}
    else:
        weights = {'keypoint_loss': 1.0, 'pelvis_loss': 0.1, 'shoulder_loss': 0.1, 'leg_symmetry_loss': 0.1, 'scale_loss': 0.2}
    return weights

# 손실 함수 정의
def calculate_loss(vertices, augmented_keypoints_3d, smpl_joints, camera, weights):
    if len(smpl_joints) != len(augmented_keypoints_3d):
        min_len = min(len(smpl_joints), len(augmented_keypoints_3d))
        smpl_joints = smpl_joints[:min_len]
        augmented_keypoints_3d = augmented_keypoints_3d[:min_len]
    projected_keypoints = camera.project(smpl_joints)
    keypoint_loss = np.sum((projected_keypoints - augmented_keypoints_3d[:, :2]) ** 2)
    vertices = smpl_joints
    pelvis_idx = [1, 2]
    shoulder_idx = [16, 17]
    left_leg_idx = [1, 4, 7]
    right_leg_idx = [2, 5, 8]
    pelvis_loss = np.sum((vertices[pelvis_idx] - np.mean(vertices[pelvis_idx], axis=0)) ** 2)
    shoulder_loss = np.sum((vertices[shoulder_idx] - np.mean(vertices[shoulder_idx], axis=0)) ** 2)
    leg_symmetry_loss = np.sum((vertices[left_leg_idx] - vertices[right_leg_idx]) ** 2)
    total_loss = (weights['keypoint_loss'] * keypoint_loss +
                  weights['pelvis_loss'] * pelvis_loss +
                  weights['shoulder_loss'] * shoulder_loss +
                  weights['leg_symmetry_loss'] * leg_symmetry_loss)
    if 'scale_loss' in weights:
        total_loss += weights['scale_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    if 'arm_length_loss' in weights:
        total_loss += weights['arm_length_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    if 'inseam_loss' in weights:
        total_loss += weights['inseam_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    if 'outseam_loss' in weights:
        total_loss += weights['outseam_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    if 'waist_loss' in weights:
        total_loss += weights['waist_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    if 'chest_loss' in weights:
        total_loss += weights['chest_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    if 'hip_loss' in weights:
        total_loss += weights['hip_loss'] * np.sum((vertices - np.mean(vertices, axis=0)) ** 2)
    return total_loss

# 최적화 루프
def smplify(augmented_keypoints_3d, smpl_model, camera, initial_params, weights):
    def loss_function(params):
        betas = torch.tensor(params[:num_betas], dtype=torch.float32).unsqueeze(0)
        body_pose = torch.tensor(params[num_betas:num_betas + smpl_model.NUM_BODY_JOINTS * 3], dtype=torch.float32).unsqueeze(0)
        global_orient = torch.tensor(params[num_betas + smpl_model.NUM_BODY_JOINTS * 3:num_betas + smpl_model.NUM_BODY_JOINTS * 3 + 3], dtype=torch.float32).unsqueeze(0)
        transl = torch.tensor(params[-3:], dtype=torch.float32).unsqueeze(0)

        smpl_output = smpl_model(betas=betas, body_pose=body_pose, global_orient=global_orient, transl=transl)
        smpl_joints = smpl_output.joints.detach().cpu().numpy().squeeze()

        loss = calculate_loss(smpl_output.vertices.detach().cpu().numpy().squeeze(), augmented_keypoints_3d, smpl_joints, camera, weights)
        return loss

    initial_params_flat = np.hstack([initial_params['betas'].flatten(), 
                                     initial_params['body_pose'].flatten(), 
                                     initial_params['global_orient'].flatten(), 
                                     initial_params['transl'].flatten()])
    
    result = minimize(loss_function, initial_params_flat, method='L-BFGS-B', options={'maxiter': 200, 'disp': True})

    optimized_params = {
        'betas': result.x[:smpl_model.num_betas].reshape(1, -1),
        'body_pose': result.x[smpl_model.num_betas:smpl_model.num_betas + smpl_model.NUM_BODY_JOINTS * 3].reshape(1, -1),
        'global_orient': result.x[smpl_model.num_betas + smpl_model.NUM_BODY_JOINTS * 3:smpl_model.num_betas + smpl_model.NUM_BODY_JOINTS * 3 + 3].reshape(1, -1),
        'transl': result.x[-3:].reshape(1, -1)
    }

    return optimized_params

def calculate_body_measurements(vertices, height, weight, bmi):
    shoulder_length = np.linalg.norm(vertices[7228] - vertices[4450]) * 100  # 어깨 길이
    arm_length = np.linalg.norm(vertices[3953] - vertices[4893]) * 100  # 팔 길이
    inseam = np.linalg.norm(vertices[3545] - vertices[8868]) * 100  # 인심
    outseam = np.linalg.norm(vertices[3489] - vertices[8868]) * 100  # 아웃심
    back_length = np.linalg.norm(vertices[5617] - vertices[5630]) * 100  # 등길이

    return {
        'height': height,
        'weight': weight,
        'BMI': bmi,
        'shoulder_length': shoulder_length,
        'arm_length': arm_length,
        'inseam': inseam,
        'outseam': outseam,
        'back_length': back_length,
    }

def calculate_circumference(vertices, indices):
    points = vertices[indices]
    points_2d = points[:, :2]
    center = np.mean(points_2d, axis=0)
    distances = np.linalg.norm(points_2d - center, axis=1)
    avg_radius = np.mean(distances)
    circumference = 2 * np.pi * avg_radius
    return circumference * 100  # cm 단위로 변환
