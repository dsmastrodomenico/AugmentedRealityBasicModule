import sys
import cv2 as cv
import numpy as np
from Webcam_Body_Tracking import BodyTrackerSystem as bts
from Camera_Calibration import CameraCalibration as cc


def _message_system(num_message):
    # menus
    if  num_message == 1.0:
        print(
            'What do you like to do?\n' +
            '   [C]alibrate.\n' +
            '   [R].\n' + 
            '   [T]racking.\n' +
            '   [E]xit.')
    

def crud_scheme():
    while True:
        command = None
        command = input('\nOption:\t').upper()
        if command == 'C':
            pass
        elif command == 'R':
            BodyTrackerSystem().start_tracking()
        elif command == 'T':
            pass
        elif command == 'E':
            break


if __name__ == "__main__":
    crud_scheme()
