
import time
import cv2
import base64
from flask_socketio import SocketIO, emit
from flask import Flask


from pathlib import Path
import argparse
import cv2
import matplotlib.cm as cm
import torch
import numpy as np
import base64
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
# import time
from models.matching import Matching
from models.utils import (AverageTimer, VideoStreamer,frame2tensor)
import itertools
torch.set_grad_enabled(False)

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
fr_wid = 480
fr_hei = 320
skip_frs = 1
# video_paths  = ["D:\\resource\\SuperGluePretrainedNetwork\\assets\\videos\\CAM_1.mp4", 'D:\\resource\\SuperGluePretrainedNetwork\\assets\\videos\\CAM_2.mp4', 'D:\\resource\\SuperGluePretrainedNetwork\\assets\\videos\\CAM_3.mp4', 'D:\\resource\\SuperGluePretrainedNetwork\\assets\\videos\\CAM_4.mp4']


def demo(video_paths, emit = None):
    print(video_paths, "+++++++++++++++++++++++++")
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
        framesCLR = []
        rets = []
        overlap = []
        # frame1, ret1 = vs1.next_frame()
        # frame2, ret2 = vs2.next_frame()
        points = matrix = [[DEFAULT for j in range(n)] for i in range(n)]
        for vs in video_streams:
            frame, frameColor, ret = vs.next_frame()
            if not ret:
                print('end')
                break
            timer = AverageTimer()
            frames.append(frame)
            framesCLR.append(frameColor)
            
            rets.append(ret)
        frame_tensors = []
        for frame  in frames:
            frame_tensors.append(frame2tensor(frame, device))
        for i in range (0,n):
            for j in range(i, n):
                if i ==j:
                    continue
                pred = matching({'image0': frame_tensors[i], 'image1': frame_tensors[j]})
                kpts0 = pred['keypoints0'][0].cpu().numpy()
                kpts1 = pred['keypoints1'][0].cpu().numpy()
                matches = pred['matches0'][0].cpu().numpy()
                confidence = pred['matching_scores0'][0].detach().cpu().numpy()
                torch.cuda.empty_cache()
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
            frames[fr] = cv2.polylines(framesCLR[fr], [np.array(overlap[fr], dtype=np.int32)],True, (0, 255, 100),1)             
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
            if n!=4:
                frx2 = np.concatenate((frx2, frames[z]), axis=1)
        framex = np.concatenate((frx1, frx2), axis=0)
        # framex = cv2.cvtColor(framex,cv2.COLOR_GRAY2RGB)
        frameBase64 = frameToBase64(framex)
        emit("estimate", frameBase64)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')



base_path = "./assets/videos/"

# define function
def frameToBase64(frame):
    # Convert the frame to a JPEG image
    _, img_encoded = cv2.imencode('.jpg', frame)
    # Convert the JPEG image to a base64-encoded string
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')
    return img_base64
# end define function

# rtsp 304    "rtsp://admin:Admin123@117.4.240.104:8084/Streaming/Channels/101/"


@socketio.on("multicamera")
def handleGetMultiPath(paths):
    global cap1
    global cap2
    global cap3
    global cap4
    cap1 = cv2.VideoCapture(base_path + paths[0])
    cap2 = cv2.VideoCapture(base_path + paths[1])
    cap3 = cv2.VideoCapture(base_path + paths[2])
    cap4 = cv2.VideoCapture(base_path + paths[3])
    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        ret3, frame3 = cap3.read()
        ret4, frame4 = cap4.read()
        if not ret1 and not ret2 and not ret3 and not ret4:
            break
        img1_base64 = frameToBase64(frame1)
        img2_base64 = frameToBase64(frame2)
        img3_base64 = frameToBase64(frame3)
        img4_base64 = frameToBase64(frame4)
        emit('test', [img1_base64, img2_base64, img3_base64, img4_base64])

@socketio.on("estimate")
def receivePathsVideo(paths):

    for i,path in enumerate(paths):
        paths[i] =  base_path + path
    # dung 4 video vuaw roi
    cap1.release()
    cap2.release()
    cap3.release()
    cap4.release()
    # ===
    print("Start estimate ___________-++_________")
    global cap
    demo(paths, emit=emit)


@socketio.on('pause')
def stop_stream_video():
    print("stopped video")
    cap1.release()
    cap2.release()
    cap3.release()
    cap4.release()
    cap.release()


if __name__ == '__main__':
    # socketio.start_background_task(emit_video_frames)
    socketio.run(app, debug=True)
