import json
import sys
import numpy as np 
import cv2 as cv
from datetime import datetime as dt
from algorithms.controller import control_camera


class CameraCalibration():
    # Crear objeto VideoCapture:
    # Create VideoCapture object:
    cap, _, _, _, _ = control_camera().InitializeCamera()


    def start_calibration_process(self):
        patw, path = 7, 6

        objp = np.zeros((patw * path, 3))
        for i in range(patw * path):
            objp[i, :2] = np.array([i % patw, i / patw], np.float32)
        objp_list, imgp_list = [], []

        while True:
            _, image = self.cap.read()

            ret, corners = cv.findChessboardCorners(image, (patw, path), None)
            cv.drawChessboardCorners(image, (patw, path), corners, ret)
            cv.imshow('Frame', image)

            key = cv.waitKey(10)
            if key == 0x1b:  # ESC
                break
            elif key == 0x20 and ret == True:
                time = dt.now()
                time = time.strftime('%d-%m-%y-%H%M%f')
                cv.imwrite('data/images/' + time + '.jpg', image)
                print('Saved!')
                objp_list.append(objp.astype(np.float32))
                imgp_list.append(corners)
                
                if len(objp_list) == 10:
                    break

        print(objp_list)
        if len(objp_list) >= 3:
            K = np.zeros((3, 3), float)
            dist = np.zeros((5, 1), float)
            ret, K, dist, rvecs, tvecs = cv.calibrateCamera(objp_list, imgp_list, (image.shape[1], image.shape[2]), None, None)
            mtx = K.tolist()
            distor = dist.tolist()

            error = 0
            for i in range(len(objp_list)):
                imgPoints2, _ = cv.projectPoints(objp_list[i], rvecs[i], tvecs[i], K, dist)
                error += cv.norm(imgp_list[i], imgPoints2, cv.NORM_L2) / len(imgPoints2)

            Error = error / len(objp_list)

            result = {
                "K": mtx,
                'Distortion': distor,
                "Error": Error
            }
            
            with open('data/calib.json', 'w') as fp:
                json.dump(result, fp, sort_keys=True, indent=4)

        else:
            print('Images are not enough')
        self.cap.release()
        # cv.destroyAllWindows()
