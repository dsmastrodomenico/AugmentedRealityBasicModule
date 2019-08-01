import sys


if __name__ == "__main__":
    print(
        'What do you like to do?\n' +
        '   [C]alibrate.\n' +
        '   [D]etection.\n' + 
        '   [T]racking.\n' +
        '   [E]xit.')

    while True:
        command = None
        command = input('\nOption:\t').upper()
        if command == 'C':
            from algorithms.calibration.Camera_Calibration import CameraCalibration
            CameraCalibration().start_calibration_process()
        elif command == 'D':
            from algorithms.recognition.Shape_Detection import ShapeDetection 
            ShapeDetection().read_process()
        elif command == 'T':
            from algorithms.tracking.Webcam_Body_Tracking import BodyTrackerSystem
            BodyTrackerSystem().start_tracking()
        elif command == 'E':
            break

