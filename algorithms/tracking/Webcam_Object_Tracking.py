import json
import sys
import cv2 as cv 
import numpy as np 
from algorithms.controller import control_camera 


class ObjectTrackerSystem():

    cap, scaling_factor, num_frames_to_track, num_frames_jump, tracking_params = control_camera().camera()

    def object_select(self): 
        # Captura el cuadro desde la camara 
        ret, self.frame = self.cap.read() 

        # Factor de submuestreo para el cuadro de entrada
        self.scaling_factor = 1 
        self.frame = cv.resize(self.frame, None, 
            fx=self.scaling_factor, fy=self.scaling_factor, interpolation=cv.INTER_AREA) 

        cv.namedWindow('Tracking de Objetos') 
        cv.setMouseCallback('Tracking de Objetos', self.mouse_event) 

        self.selection = None 
        self.drag_start = None 
        self.tracking_state = 0 


    # Metodo para rastrear eventos del mouse
    def mouse_event(self, event, x, y, flags, param): 
        x, y = np.int16([x, y]) 

        # Detectar el evento del movimiento del boton del mouse hacia abajo
        if event == cv.EVENT_LBUTTONDOWN: 
            self.drag_start = (x, y) 
            self.tracking_state = 0 

        if self.drag_start:
            if event == cv.EVENT_MOUSEMOVE:
                h, w = self.frame.shape[:2] 
                xo, yo = self.drag_start 
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y])) 
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y])) 
                self.selection = None 

                if x1-x0 > 0 and y1-y0 > 0:
                    self.selection = (x0, y0, x1, y1) 

            elif event == cv.EVENT_LBUTTONUP:
                self.drag_start = None 
                if self.selection is not None: 
                    self.tracking_state = 1 


    # Definicion del metodo para iniciar el seguimiento del objeto.
    def start_tracking(self): 
        # Seccion para repetir hasta que el usuario presione la tecla Esc. 
        while True: 
            # Captura el cuadro desde la camara
            ret, self.frame = self.cap.read() 
            # Cambiar el tamano del marco de entrada
            self.frame = cv.resize(self.frame, None,
                fx=self.scaling_factor, fy=self.scaling_factor, interpolation=cv.INTER_AREA) 

            vis = self.frame.copy() 

            # Convercion de color HSV
            hsv = cv.cvtColor(self.frame, cv.COLOR_BGR2HSV) 

            # Crea una mascara basada en umbrales predefinidos.
            mask = cv.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.))) 

            if self.selection: 
                x0, y0, x1, y1 = self.selection 
                self.track_window = (x0, y0, x1-x0, y1-y0) 
                hsv_roi = hsv[y0:y1, x0:x1] 
                mask_roi = mask[y0:y1, x0:x1] 

                # Calcular el histograma 
                hist = cv.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] ) 

                # Normalizar y remodelar el histograma. 
                cv.normalize(hist, hist, 0, 255, cv.NORM_MINMAX); 
                self.hist = hist.reshape(-1) 

                vis_roi = vis[y0:y1, x0:x1] 
                cv.bitwise_not(vis_roi, vis_roi) 
                vis[mask == 0] = 0 

            if self.tracking_state == 1:
                self.selection = None 

                # Calcular la proyeccion posterior del histograma.
                prob = cv.calcBackProject([hsv], [0], self.hist, [0, 180], 1) 

                prob &= mask 
                term_crit = ( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1 ) 

                # Aplicar CAMShift en 'prob' 
                track_box, self.track_window = cv.CamShift(prob, self.track_window, term_crit) 

                # Dibuja una elipse alrededor del objeto.
                cv.ellipse(vis, track_box, (0, 255, 0), 2) 

            cv.imshow('Tracking de Objetos', vis) 

            c = cv.waitKey() 
            if c == 27: 
                break 

        cv.destroyAllWindows() 