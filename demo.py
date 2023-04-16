from pathlib import Path
import argparse
import cv2
import matplotlib.cm as cm
import torch

from models.matching import Matching
from models.utils import (AverageTimer, VideoStreamer,
                          make_matching_plot_fast, frame2tensor)


torch.set_grad_enabled(False)


device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Running inference on device \"{}\"'.format(device))

config = {
        'superpoint': {
            'nms_radius': 4,
            'keypoint_threshold': 0.005,
            'max_keypoints': 1500
        },
        'superglue': {
            'weights': 'indoor',
            'sinkhorn_iterations': 20,
            'match_threshold': 0.005,
        }
    }

matching = Matching(config).eval().to(device)

keys = ['keypoints', 'scores', 'descriptors']

vs1 = VideoStreamer('D:\\resource\\SuperGluePretrainedNetwork\\match_vid\\1.mp4', [640,480], 5,
                       ['*.png', '*.jpg', '*.jpeg'], 100000)
vs2 = VideoStreamer('D:\\resource\\SuperGluePretrainedNetwork\\match_vid\\3.mp4', [640,480], 5,
                       ['*.png', '*.jpg', '*.jpeg'], 100000)

cv2.namedWindow('SuperGlue matches', cv2.WINDOW_NORMAL)
cv2.resizeWindow('SuperGlue matches', 640*2, 480)
timer = AverageTimer()
while True :
    frame1, ret1 = vs1.next_frame()
    frame2, ret2 = vs2.next_frame()

    if not ret1 or not ret2 :
            print('Finished demo')
            break

    frame_tensor1 = frame2tensor(frame1, device)
    frame_tensor2 = frame2tensor(frame2, device)

    pred = matching({'image0': frame_tensor1, 'image1': frame_tensor2})
    kpts0 = pred['keypoints0'][0].cpu().numpy()
    kpts1 = pred['keypoints1'][0].cpu().numpy()
    matches = pred['matches0'][0].cpu().numpy()
    confidence = pred['matching_scores0'][0].cpu().numpy()
    timer.update('forward')

    valid = matches > -1
    mkpts0 = kpts0[valid]
    mkpts1 = kpts1[matches[valid]]
    color = cm.jet(confidence[valid])

    text = [
            'SuperGlue',
            'Keypoints: {}:{}'.format(len(kpts0), len(kpts1)),
            'Matches: {}'.format(len(mkpts0))
        ]


    k_thresh = matching.superpoint.config['keypoint_threshold']
    m_thresh = matching.superglue.config['match_threshold']

    
    small_text = [
            'Keypoint Threshold: {:.4f}'.format(k_thresh),
            'Match Threshold: {:.2f}'.format(m_thresh),
        ]

    print(mkpts0, mkpts0.shape)
    out = make_matching_plot_fast(
            frame1, frame2, kpts0, kpts1, mkpts0, mkpts1, color, text,
            path=None, show_keypoints=True, small_text=small_text, matched = False, overlap=True)
    
    cv2.imshow('SuperGlue matches', out)
    key = chr(cv2.waitKey(0) & 0xFF)

    if key == 'q':
                vs1.cleanup()
                vs2.cleanup()
                print('Exiting (via q) demo_superglue.py')
                break
    
    cv2.destroyAllWindows()
    vs1.cleanup()
    vs2.cleanup()