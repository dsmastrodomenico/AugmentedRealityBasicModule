import time
import cv2 as cv
import numpy as np
import pickle as pkl
from algorithms.controller import control_camera


class CameraCalibration():
    # Crear objeto VideoCapture:
    # Create VideoCapture object:
    cap, _, _, _, _ = control_camera().InitializeCamera()

    def create_dictionary_board(self):
        # Crear diccionario y objeto de pizarra:
        # Create dictionary and board object:
        self.dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_7X7_250)
        self.board = cv.aruco.CharucoBoard_create(3, 3, .025, .0125, self.dictionary)

        return self.board, self.dictionary
        
    def write_dictionary_image_board(self):
        board, _ = CameraCalibration().create_dictionary_board()

        # Crear imagen de tablero para usar en el proceso de calibración:
        # Create board image to be used in the calibration process:
        image_board = board.draw((200 * 3, 200 * 3))

        # Escribir imagen de la placa de calibración:
        # Write calibration board image:
        cv.imwrite('image.png', image_board)

    def calibration_process(self):
        cal = None
        all_corners = []
        all_ids = []
        counter = 0
        board, dictionary = CameraCalibration().create_dictionary_board()

        for i in range(300):

            # Read frame from the webcam:
            ret, frame = self.cap.read()

            # Convert to grayscale:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            # Detect markers:
            res = cv.aruco.detectMarkers(gray, dictionary)

            if len(res[0]) > 0:
                res2 = cv.aruco.interpolateCornersCharuco(res[0], res[1], gray, board)
                if res2[1] is not None and res2[2] is not None and len(res2[1]) > 3 and counter % 3 == 0:
                    all_corners.append(res2[1])
                    all_ids.append(res2[2])

                cv.aruco.drawDetectedMarkers(gray, res[0], res[1])

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

            counter += 1

        try:
            cal = cv.aruco.calibrateCameraCharuco(all_corners, all_ids, board, gray.shape, None, None)
        except:
            self.cap.release()
            print("Calibration could not be done ...")

        # Obtenga el resultado de la calibración:
        # Get the calibration result:
        if cal != None:
            retval, cameraMatrix, distCoeffs, rvecs, tvecs = cal
        
            # Guardar los parámetros de la cámara:
            # Save the camera parameters:
            f = open('calibration.pckl', 'wb')
            pkl.dump((cameraMatrix, distCoeffs), f)
            f.close()
            self.cap.release()