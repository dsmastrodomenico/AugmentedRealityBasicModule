import json
import sys
import cv2 as cv 
import numpy as np 
from algorithms.controller import control_camera 


class BackgroundSubstraction():
    cap, scaling_factor, _, _, _ = control_camera().camera()

    # Captura el cuadro de entrada
    def get_frame(self, cap, scaling_factor=0.5): 
        ret, frame = self.cap.read() 

        # Cambiar el tamaño del marco
        frame = cv.resize(frame, None, fx=scaling_factor, 
                fy=scaling_factor, interpolation=cv.INTER_AREA) 

        return frame 

    def substraction(self):
        # Crear el objeto restador de fondo
        bgSubtractor = cv.createBackgroundSubtractorMOG2()

        # Este factor controla la tasa de aprendizaje del algoritmo. La tasa de aprendizaje se refiere a la tasa a la que su modelo aprenderá 
        # sobre el fondo. Un valor más alto para 'historia' indica una tasa de aprendizaje más lenta. Puedes jugar con este parámetro para 
        # ver cómo afecta la salida.
        history = 100 

        # Iterar hasta que el usuario presione la tecla ESC
        while True: 
            frame = self.get_frame(self.cap, 0.5) 

            # Aplicar el modelo de resta de fondo al marco de entrada
            mask = bgSubtractor.apply(frame, learningRate=1.0/history)

            # Convertir de escala de grises a RGB de 3 canales 
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR) 

            cv.imshow('Input frame', frame)
            cv.imshow('Moving Objects MOG', mask & frame)

            # Compruebe si el usuario presionó la tecla ESC 
            c = cv.waitKey(delay=30) 
            if c == 27: 
                break 

        self.cap.release() 
        cv.destroyAllWindows()