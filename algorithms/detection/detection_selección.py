import cv2 as cv
import os
import pickle as pkl
import numpy as np
from collections import namedtuple 
from algorithms.controller import control_camera

class ROISelector(object): 
    def __init__(self, win_name, init_frame, callback_func): 
        self.callback_func = callback_func 
        self.selected_rect = None 
        self.drag_start = None 
        self.tracking_state = 0
        event_params = {"frame": init_frame}
        cv.namedWindow(win_name)
        cv.setMouseCallback(win_name, self.mouse_event, event_params)

    def mouse_event(self, event, x, y, flags, param):
        x, y = np.int16([x, y]) 

        
        if event == cv.EVENT_LBUTTONDOWN: 
            self.drag_start = (x, y) 
            self.tracking_state = 0 

        if self.drag_start:
            if event == cv.EVENT_MOUSEMOVE:
                h, w = param["frame"].shape[:2] 
                xo, yo = self.drag_start 
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y])) 
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y])) 
                self.selected_rect = None 

                if x1-x0 > 0 and y1-y0 > 0:
                    self.selected_rect = (x0, y0, x1, y1) 

            elif event == cv.EVENT_LBUTTONUP:
                self.drag_start = None 
                if self.selected_rect is not None: 
                    self.callback_func(self.selected_rect)
                    self.selected_rect = None
                    self.tracking_state = 1

