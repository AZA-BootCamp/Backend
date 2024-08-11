import sys
import os
import subprocess
import numpy as np
import cv2
import torch
from fastapi import HTTPException

# sys.path에 프로젝트의 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.lightweight_human.models.with_mobilenet import PoseEstimationWithMobileNet
from model.lightweight_human.modules.keypoints import extract_keypoints, group_keypoints
from model.lightweight_human.modules.load_state import load_state
from model.lightweight_human.modules.pose import Pose
import model.lightweight_human.demo as demo


def get_rect(net, images, height_size):
    net = net.eval()

    stride = 8
    upsample_ratio = 4
    num_keypoints = Pose.num_kpts

    for image in images:
        rect_path = image.replace('.%s' % (image.split('.')[-1]), '_rect.txt')
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        orig_img = img.copy()
        heatmaps, pafs, scale, pad = demo.infer_fast(net, img, height_size, stride, upsample_ratio, cpu=True)

        total_keypoints_num = 0
        all_keypoints_by_type = []
        for kpt_idx in range(num_keypoints):  # 19th for bg
            total_keypoints_num += extract_keypoints(heatmaps[:, :, kpt_idx], all_keypoints_by_type, total_keypoints_num)

        pose_entries, all_keypoints = group_keypoints(all_keypoints_by_type, pafs)
        for kpt_id in range(all_keypoints.shape[0]):
            all_keypoints[kpt_id, 0] = (all_keypoints[kpt_id, 0] * stride / upsample_ratio - pad[1]) / scale
            all_keypoints[kpt_id, 1] = (all_keypoints[kpt_id, 1] * stride / upsample_ratio - pad[0]) / scale

        rects = []
        for n in range(len(pose_entries)):
            if len(pose_entries[n]) == 0:
                continue
            pose_keypoints = np.ones((num_keypoints, 2), dtype=np.int32) * -1
            valid_keypoints = []
            for kpt_id in range(num_keypoints):
                if pose_entries[n][kpt_id] != -1.0:  # keypoint was found
                    pose_keypoints[kpt_id, 0] = int(all_keypoints[int(pose_entries[n][kpt_id]), 0])
                    pose_keypoints[kpt_id, 1] = int(all_keypoints[int(pose_entries[n][kpt_id]), 1])
                    valid_keypoints.append([pose_keypoints[kpt_id, 0], pose_keypoints[kpt_id, 1]])
            valid_keypoints = np.array(valid_keypoints)

            if pose_entries[n][10] != -1.0 or pose_entries[n][13] != -1.0:
                pmin = valid_keypoints.min(0)
                pmax = valid_keypoints.max(0)
                center = (0.5 * (pmax[:2] + pmin[:2])).astype(int)
                radius = int(0.65 * max(pmax[0]-pmin[0], pmax[1]-pmin[1]))
            elif pose_entries[n][10] == -1.0 and pose_entries[n][13] == -1.0 and pose_entries[n][8] != -1.0 and pose_entries[n][11] != -1.0:
                center = (0.5 * (pose_keypoints[8] + pose_keypoints[11])).astype(int)
                radius = int(1.45 * np.sqrt(((center[None, :] - valid_keypoints)**2).sum(1)).max(0))
                center[1] += int(0.05 * radius)
            else:
                center = np.array([img.shape[1] // 2, img.shape[0] // 2])
                radius = max(img.shape[1] // 2, img.shape[0] // 2)

            x1 = center[0] - radius
            y1 = center[1] - radius

            rects.append([x1, y1, 2 * radius, 2 * radius])

        np.savetxt(rect_path, np.array(rects), fmt='%d')

def initialize_pose_estimation_model():
    try:
        image_path = "/Users/heejin/Downloads/Backend/backend/fastapi_app/uploaded_files"
        image = image_path[0]
        print(f"Initializing pose estimation model with image: {image}")
        checkpoint_path = '/Users/heejin/Downloads/Backend/backend/fastapi_app/model/lightweight_human/checkpoint_iter_370000.pth'
        
        # 모델 초기화 및 체크포인트 로드
        net = PoseEstimationWithMobileNet()
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
        print("Checkpoint loaded successfully")
        
        load_state(net, checkpoint)
        print("Model state loaded successfully")
        
        # get_rect 함수 호출
        get_rect(net.cpu(), [image], 512)  # CPU 모드로 실행
        print("get_rect function executed successfully")
    
    except Exception as e:
        print(f"Error in pose estimation model initialization: {e}")
        raise HTTPException(status_code=500, detail=f"Pose estimation model initialization failed: {e}")


    ''' 
    gpu 사용
    try:
        print(f"Initializing pose estimation model with image: {image_path}")
        net = PoseEstimationWithMobileNet()
        checkpoint = torch.load('/Users/heejin/Downloads/Backend/backend/fastapi_app/model/lightweight_human/checkpoint_iter_370000.pth', map_location='cpu', weights_only=True)
        load_state(net, checkpoint)
        get_rect(net.cuda(), [image_path[0]], 512)
    except Exception as e:
        print(f"Error in pose estimation model initialization: {e}")
        raise HTTPException(status_code=500, detail=f"Pose estimation model initialization failed: {e}")
    '''

def process_image_with_pifuhd():
    try:
        image_path = "/Users/heejin/Downloads/Backend/backend/fastapi_app/uploaded_files"
        print(f"Processing image with PIFuHD: {image_path}")
        os.chdir("/Users/heejin/Downloads/Backend/backend/fastapi_app/model/pifuhd")
        subprocess.run(["python", "-m", "apps.simple_test", "-r", "256", "--use_rect", "-i", image_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"PIFuHD model execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"PIFuHD model execution failed: {e}")
    except Exception as e:
        print(f"Unexpected error during PIFuHD processing: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error during PIFuHD processing: {e}")


