import sys
import cv2 as cv
import numpy as np
import json
from algorithms.controller import control_camera 


class ShapeDetection():

    cap, scaling_factor, _, _, _ = control_camera().camera()


    def setPoints(self, event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONDOWN:
            points.append((x, y))
            recording = False
            print(recording)


    def read_process(self):
        cv.namedWindow("Frame")
        cv.setMouseCallback("Frame", self.setPoints)

        points = []
        recording = True
        while True:
            if recording:
                # leer el marco de entrada 
                _, frame = self.cap.read()

                # bajar la muestra del marco de entrada 
                frame = cv.resize(frame, None, fx=self.scaling_factor, fy=self.scaling_factor,
                    interpolation=cv.INTER_AREA)

                frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

                corners = cv.goodFeaturesToTrack(frame_gray, 300, 0.05, 10)

                if corners is not None:
                    corners = np.int0(corners)
                    for corner in corners:
                        x, y = corner.ravel()
                        cv.circle(frame, (x, y), 3, (0, 0, 255), -1)

            cv.imshow("Frame", frame)

            for point in points:
                cv.circle(frame, point, 3, (255, 0, 0), -1)

            key = cv.waitKey(1)
            if key == 27:
                break
            elif key == ord("p"):
                recording = False
            elif key == ord("c"):
                recording = True
            elif key == ord("s"):
                if corners is not None:
                    with open('resources/coords.txt', 'w') as coords_file:
                        corners = np.int0(corners)
                        for corner in corners:
                            np.savetxt(coords_file, corner, fmt='%-4d')

                if points is not None:
                    print(points)
                    with open('resources/points.txt', 'w') as txtPoints:
                        npPoints = np.int0(points)
                        np.savetxt(txtPoints, npPoints, fmt='%-4d')
        self.cap.release()
        cv.destroyAllWindows()
