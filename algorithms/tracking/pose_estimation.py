import cv2 as cv
import os
import pickle as pkl
import numpy as np
from collections import namedtuple 
from algorithms.controller import control_camera
from algorithms.tracking.pose_estimation import PoseEstimator

class PoseEstimator(object): 
    def __init__(self): 
        
        flann_params = dict(algorithm = 6, table_number = 6, key_size = 12, multi_probe_level = 1) 

        self.min_matches = 10 
        self.cur_target = namedtuple('Current', 'image, rect, keypoints, descriptors, data')
        self.tracked_target = namedtuple('Tracked', 'target, points_prev, points_cur, H, quad') 

        self.feature_detector = cv.ORB_create()
        self.feature_detector.setMaxFeatures(1000)
        self.feature_matcher = cv.FlannBasedMatcher(flann_params, {}) 
        self.tracking_targets = [] 

    
    def add_target(self, image, rect, data=None): 
        x_start, y_start, x_end, y_end = rect 
        keypoints, descriptors = [], [] 
        for keypoint, descriptor in zip(*self.detect_features(image)): 
            x, y = keypoint.pt 
            if x_start <= x <= x_end and y_start <= y <= y_end: 
                keypoints.append(keypoint) 
                descriptors.append(descriptor) 

        descriptors = np.array(descriptors, dtype='uint8') 
        self.feature_matcher.add([descriptors]) 
        target = self.cur_target(image=image, rect=rect, keypoints=keypoints, descriptors=descriptors, data=None) 
        self.tracking_targets.append(target) 

     
    def track_target(self, frame): 
        self.cur_keypoints, self.cur_descriptors = self.detect_features(frame) 

        if len(self.cur_keypoints) < self.min_matches: return []
        try: matches = self.feature_matcher.knnMatch(self.cur_descriptors, k=2)
        except Exception as e:
            print('Invalid target, please select another with features to extract')
            return []
        matches = [match[0] for match in matches if len(match) == 2 and match[0].distance < match[1].distance * 0.75] 
        if len(matches) < self.min_matches: return [] 

        matches_using_index = [[] for _ in range(len(self.tracking_targets))] 
        for match in matches: 
            matches_using_index[match.imgIdx].append(match) 

        tracked = [] 
        for image_index, matches in enumerate(matches_using_index): 
            if len(matches) < self.min_matches: continue 

            target = self.tracking_targets[image_index] 
            points_prev = [target.keypoints[m.trainIdx].pt for m in matches]
            points_cur = [self.cur_keypoints[m.queryIdx].pt for m in matches]
            points_prev, points_cur = np.float32((points_prev, points_cur))
            H, status = cv.findHomography(points_prev, points_cur, cv.RANSAC, 3.0) 
            status = status.ravel() != 0

            if status.sum() < self.min_matches: continue 

            points_prev, points_cur = points_prev[status], points_cur[status] 

            x_start, y_start, x_end, y_end = target.rect 
            quad = np.float32([[x_start, y_start], [x_end, y_start], [x_end, y_end], [x_start, y_end]])
            quad = cv.perspectiveTransform(quad.reshape(1, -1, 2), H).reshape(-1, 2)
            track = self.tracked_target(target=target, points_prev=points_prev, points_cur=points_cur, H=H, quad=quad) 
            tracked.append(track) 

        tracked.sort(key = lambda x: len(x.points_prev), reverse=True) 
        return tracked 

    
    def detect_features(self, frame): 
        keypoints, descriptors = self.feature_detector.detectAndCompute(frame, None) 
        if descriptors is None: descriptors = [] 
        return keypoints, descriptors 

    
    def clear_targets(self): 
        self.feature_matcher.clear() 
        self.tracking_targets = [] 