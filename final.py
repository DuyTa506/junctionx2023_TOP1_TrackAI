from pathlib import Path
import argparse
import cv2
import matplotlib.cm as cm
import torch
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
# import time
from models.matching import Matching
from models.utils import (AverageTimer, VideoStreamer,
                          make_matching_plot_fast, frame2tensor)
import itertools
import os
# import enumerate
torch.set_grad_enabled(False)
def get_files(root_dir):
    files = []
    for subdir, dirs, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(subdir, filename)
            files.append(file_path)
    return files
def intersection(hulls):
    result = hulls[0]
    for i in range(1, len(hulls)):
        try:
            result = result.intersection(hulls[i])
        except Exception as e:
            print(e)
            result = DEFAULT

    # Sắp xếp kết quả theo chiều kim đồng hồ
    try:
        # tồn tại vùng giao diện tích > 0
        result = result.exterior.coords[::-1]
        return (result)
    except AttributeError:
        return 0

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Running inference on device \"{}\"'.format(device))

config = {
        'superpoint': {
            'nms_radius': 1,
            'keypoint_threshold': 0.005,
            'max_keypoints': 1500
        },
        'superglue': {
            'weights': '30epoch',
            'sinkhorn_iterations': 50,
            'match_threshold': 0.12,
        }
    }

matching = Matching(config).eval().to(device)

keys = ['keypoints', 'scores', 'descriptors']
fr_wid = 1920
fr_hei = 1080
skip_frs = 1
video_paths  = ['match_vid/Public_Test/videos/scene_dynamic_cam_01/CAM_1.mp4', 'match_vid/Public_Test/videos/scene_dynamic_cam_01/CAM_2.mp4', 'match_vid/Public_Test/videos/scene_dynamic_cam_01/CAM_3.mp4', 'match_vid/Public_Test/videos/scene_dynamic_cam_01/CAM_4.mp4']

def infer(parent_folder):
    parent_name = parent_folder.split("/")[-1]
    print(parent_name)
    output_folder = os.path.join("groundtruth2", parent_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    video_paths = get_files(parent_folder) 
    n = len(video_paths)
    video_streams = []
    for video_path in video_paths:
        vs = VideoStreamer(video_path, [fr_wid, fr_hei], skip_frs, ['*.png', '*.jpg', '*.jpeg'], 100000)
        video_streams.append(vs)
    DEFAULT = np.array([[0, 0],  [640, 0], [640, 480],[480, 0]])
    overlaps =[]
    timer = AverageTimer()
    matching_key_points = []
    index = 1
    while True :
        frame_name = "frame_"+ str(index)+".jpg"
        index +=1
        frames = []
        rets = []
        overlap = []
        # frame1, ret1 = vs1.next_frame()
        # frame2, ret2 = vs2.next_frame()
        points = matrix = [[DEFAULT for j in range(n)] for i in range(n)]
        for vs in video_streams:
            frame,_ , ret = vs.next_frame()
            if not ret:
                print('end')
                return
            timer = AverageTimer(nums=n)
            frames.append(frame)
            rets.append(ret)
        frame_tensors = []
        for frame in frames:
            frame_tensors.append(frame2tensor(frame, device))
        for i in range (0,n):
            for j in range(i, n):
                if i ==j:
                    continue
                pred = matching({'image0': frame_tensors[i], 'image1': frame_tensors[j]})
                kpts0 = pred['keypoints0'][0].cpu().numpy()
                kpts1 = pred['keypoints1'][0].cpu().numpy()
                matches = pred['matches0'][0].cpu().numpy()
                confidence = pred['matching_scores0'][0].cpu().numpy()
                valid = matches > -1
                mkpts0 = kpts0[valid]
                mkpts1 = kpts1[matches[valid]]
                if len(mkpts0) <3:
                    hull0 = DEFAULT
                    hull1 = DEFAULT
                else:
                    hull0 = cv2.convexHull(mkpts0)
                    hull1 = cv2.convexHull(mkpts1)
                    hull0= list(itertools.chain(*hull0))
                    hull1= list(itertools.chain(*hull1))
                points[i][j] = hull0
                points[j][i] = hull1
        for i in range(0,n):
            hulls = []
            for j in range(0,n):
                if i == j:
                    continue
                hulls.append(Polygon(points[i][j]))
            tt = intersection(hulls)
            # Chuyển đổi danh sách tọa độ thành mảng numpy
            tt= np.array(tt)
            try:
                overlap.append(tt[:-1])
            except:
                overlap.append(DEFAULT)
        timer.update('overlap process')
        
        fps = timer.print()
        for idx, item in enumerate(overlap):
            cam_name = "CAM_"+ str(int(idx)+1)+".txt"
            string = "("
            for lo in item:
                for l in lo:
                    # print(type(l)
                    string += str(round(l*4))+","
            string = string[:-1]+"), "
            string= frame_name+ " "+string+str(fps)
            with open(os.path.join(output_folder, cam_name), "a") as f:
                f.write(string)
                f.write("\n")              
        overlaps.append(overlap)
    print("done")
    return

if __name__ == '__main__':
    infer(video_paths)




