import cv2 as cv
import os
import pickle as pkl
import numpy as np
from collections import namedtuple 
from algorithms.detection.detection_selección import ROISelector
from algorithms.tracking.pose_estimation import PoseEstimator
from algorithms.controller import control_camera


class startTracking(object): 
    def __init__(self): 
        cap, scaling_factor, _, _, _ = control_camera().InitializeCamera()
        self.cap = cap 
        self.rect = None
        self.win_name = 'Augmented Reality'
        self.scaling_factor = scaling_factor
        self.tracker = PoseEstimator() 

        ret, frame = self.cap.read()
        self.rect = None
        self.frame = cv.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv.INTER_AREA)

        self.roi_selector = ROISelector(self.win_name, self.frame, self.set_rect)
        self.overlay_vertices = np.float32([[0, 0, 0], [0, 1, 0], [1, 1, 0],
            [1, 0, 0], [0.5, 0.5, 4]]) 
        self.overlay_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0,4), (1,4), (2,4), (3,4)] 
        self.color_base = (0, 255, 0) 
        self.color_lines = (0, 0, 0) 

        self.overlay_vertices = np.float32([[0, 0, 0], [0, 1, 0], [1, 1, 0],
            [1, 0, 0], [0.5, 0.5, 4]]) 
        self.overlay_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0,4), (1,4), (2,4), (3,4)] 
        self.color_base = (0, 255, 0) 
        self.color_lines = (0, 0, 0) 
 
        self.graphics_counter = 0 
        self.time_counter = 0 


    def set_rect(self, rect): 
        self.rect = rect
        self.tracker.add_target(self.frame, rect) 


    def start(self): 
        paused = False
        while True:
            if not paused or self.frame is None: 
                ret, frame = self.cap.read() 
                scaling_factor = self.scaling_factor
                frame = cv.resize(frame, None, fx=scaling_factor, fy=scaling_factor,\
                    interpolation=cv.INTER_AREA) 
                if not ret: break 

                self.frame = frame.copy() 

            img = self.frame.copy() 
            if not paused: 
                tracked = self.tracker.track_target(self.frame) 
                for item in tracked: 
                    cv.polylines(img, [np.int32(item.quad)], 
                     True, self.color_lines, 2) 
                    for (x, y) in np.int32(item.points_cur): 
                        cv.circle(img, (x, y), 2, 
                         self.color_lines) 

                    self.overlay_graphics(img, item) 
 
            cv.imshow(self.win_name, img) 
            ch = cv.waitKey(1) 
            if ch == ord('c'): self.tracker.clear_targets() 
            if ch == 27: break 


    def overlay_graphics(self, img, tracked):
        x_start, y_start, x_end, y_end = tracked.target.rect 
        quad_3d = np.float32([[x_start, y_start, 0], [x_end, 
         y_start, 0], 
                    [x_end, y_end, 0], [x_start, y_end, 0]]) 
        h, w = img.shape[:2] 
        K = np.float64([[w, 0, 0.5*(w-1)], 
                        [0, w, 0.5*(h-1)], 
                        [0, 0, 1.0]]) 
        dist_coef = np.zeros(4) 
        ret, rvec, tvec = cv.solvePnP(objectPoints=quad_3d, imagePoints=tracked.quad,
                                       cameraMatrix=K, distCoeffs=dist_coef)
        verts = self.overlay_vertices * \
            [(x_end-x_start), (y_end-y_start), -(x_end-x_start)*0.3] + (x_start, y_start, 0) 
        verts = cv.projectPoints(verts, rvec, tvec, cameraMatrix=K,
                                  distCoeffs=dist_coef)[0].reshape(-1, 2)

        verts_floor = np.int32(verts).reshape(-1,2) 
        cv.drawContours(img, contours=[verts_floor[:4]],
             contourIdx=-1, color=self.color_base, thickness=-3)
        cv.drawContours(img, contours=[np.vstack((verts_floor[:2],
            verts_floor[4:5]))], contourIdx=-1, color=(0,255,0), thickness=-3)
        cv.drawContours(img, contours=[np.vstack((verts_floor[1:3],
            verts_floor[4:5]))], contourIdx=-1, color=(255,0,0), thickness=-3)
        cv.drawContours(img, contours=[np.vstack((verts_floor[2:4], 
            verts_floor[4:5]))], contourIdx=-1, color=(0,0,150), thickness=-3)
        cv.drawContours(img, contours=[np.vstack((verts_floor[3:4],
            verts_floor[0:1], verts_floor[4:5]))], contourIdx=-1, color=(255,255,0),thickness=-3)

        for i, j in self.overlay_edges: 
            (x_start, y_start), (x_end, y_end) = verts[i], verts[j]
            cv.line(img, (int(x_start), int(y_start)), (int(x_end), int(y_end)),     
                self.color_lines, 2)