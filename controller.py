import json
import sys
import cv2 as cv 
import numpy as np 

class control_camera(): 
    def camera(self):
        # Captura el marco de entrada 
        cap = cv.VideoCapture(0) 

        # Factor de submuestreo para la imagen. 
        scaling_factor = 1 

        # Numero de cuadros para mantener en el bufer cuando realiza el seguimiento. Si aumenta este numero, los puntos de caracteristica tendran mas "inercia"
        num_frames_to_track = 50 

        # Saltar cada 'n' cuadros. Esto es solo para aumentar la velocidad.
        num_frames_jump = 20 

        # 'winSize' se refiere al tamano de cada parche. Estos parches son los bloques mas pequenos en los que operamos y rastreamos los puntos de caracteristicas.
        tracking_params = dict(winSize = (11, 11), maxLevel = 2, 
            criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03)) 
        
        return cap, scaling_factor, num_frames_to_track, num_frames_jump, tracking_params