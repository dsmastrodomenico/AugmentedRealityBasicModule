import sys
from algorithms.calibration.Camera_Calibration import CameraCalibration
from algorithms.tracking.Webcam_Body_Tracking import BodyTrackerSystem 

if __name__ == "__main__":
    print(
        'What do you like to do?\n' +
        '   [C]alibrate.\n' +
        '   [R]e.\n' + 
        '   [T]racking.\n' +
        '   [E]xit.')

    while True:
        command = None
        command = input('\nOption:\t').upper()
        if command == 'C':
            CameraCalibration().start_calibration_process()
        elif command == 'R':
            pass
        elif command == 'T':
            BodyTrackerSystem().start_tracking()
        elif command == 'E':
            break
