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
from models.utils import (AverageTimer, VideoStreamer,frame2tensor)
import base64
import itertools
torch.set_grad_enabled(False)


# define function

def frameToBase64(frame):
    # Convert the frame to a JPEG image
    _, img_encoded = cv2.imencode('.jpg', frame)
    # Convert the JPEG image to a base64-encoded string
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    return img_base64

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
    
#  end define

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Running inference on device \"{}\"'.format(device))

config = {
        'superpoint': {
            'nms_radius': 3,
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
video_paths  = ['D:\\resource\\SuperGluePretrainedNetwork\\Public_Test\\videos\\scene2cam_01\\CAM_1.mp4', 'D:\\resource\\SuperGluePretrainedNetwork\\Public_Test\\videos\\scene2cam_01\\CAM_2.mp4']


def demo(video_paths, emit):
    n = len(video_paths)
    video_streams = []
    for video_path in video_paths:
        vs = VideoStreamer(video_path, [fr_wid, fr_hei], skip_frs, ['*.png', '*.jpg', '*.jpeg'], 100000)
        video_streams.append(vs)
    DEFAULT = np.array([[0, 0],  [fr_wid, 0], [fr_wid, fr_hei],[fr_hei, 0]])

    # cv2.namedWindow('SuperGlue matches', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('SuperGlue matches', 1080*2, 720)
    overlaps_list =[]

    matching_key_points = []
    while True :
        frames = []
        rets = []
        overlap = []
        # frame1, ret1 = vs1.next_frame()
        # frame2, ret2 = vs2.next_frame()
        points = matrix = [[DEFAULT for j in range(n)] for i in range(n)]
        for vs in video_streams:
            frame, ret = vs.next_frame()
            if not ret:
                print('end')
                break
            timer = AverageTimer()
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
            
            

        for fr in range(0,n):
            frames[fr] = cv2.polylines(frames[fr], [np.array(overlap[fr], dtype=np.int32)],True, (0, 255, 100),1)             
        framex = frames[0]
        frx1 = framex
        frx2 = framex
        for z in range(1,n):
            if z==1:
                frx1 = np.concatenate((framex, frames[z]), axis=1)
            elif z==2:
                frx2 = frames[z]
                # np.concatenate((framex, frames[z]), axis=0)
            elif z==3:
                frx2 = np.concatenate((frx2, frames[z]), axis=1)
            if (n !=4):
                frx2 = np.concatenate((frx2, frames[z]), axis=1)
        framex = np.concatenate((frx1, frx2), axis=0)
        img_base64 = frameToBase64(framex)
        emit('estimate', img_base64)
    # show_overlap = true
    # temp = timer.print()
    # overlaps_list.append(temp)
    # if show_overlap :
    #     cv2.imshow('image', framex)
    #     key = chr(cv2.waitKey(0) & 0xFF)
    #     if key == 'q':
    #         for v in video_streams:
    #             v.cleanup()
    #         print('Exiting (via q) demo_superglue.py')
    #         break
    #     cv2.destroyAllWindows()
    #     for v in video_streams:
    #         v.cleanup()
    # print(overlaps_list)    


