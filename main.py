import sys
import json
from algorithms.controller import control_camera
from algorithms.calibration.Aruco_Cam_Calibration import CameraCalibration
from algorithms.tracking.tracking_process import startTracking

class augmentedRealityProcess():

    @classmethod
    def main(cls):
        CameraCalibration().calibration_process()         
        startTracking().start()


if __name__ == "__main__":
    augmentedRealityProcess.main()